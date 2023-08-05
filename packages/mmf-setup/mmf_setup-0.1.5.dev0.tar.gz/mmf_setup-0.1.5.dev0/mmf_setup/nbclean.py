"""Mercurial extension for committing clean Jupyter notebooks.

Development Notes:

Tags vs Bookmarks: At several points we need to mark changesets.  Tags
  seem like the correct thing to do, but one cannot tag the null
  revision.  This means we must go through some contortions to get our
  code to work on an empty repo.  Instead, we use bookmarks.  The
  potential problem with bookmarks is that they are like branches - if
  you make commits on top, the bookmark will advance.  This can be
  disabled by making sure the bookmarks are inactive.  Since the null
  revision can be bookmarked, this simplifies our code.

API vs hglib: This code contains two paths of execution.  One use the
  Mercurial API and the other uses the hglib module.

  Mercurial API:
    Advantages:
      * Faster (not much though 12s instead of 10s for test suite)
      * More flexible (full access to internals)
    Disadvantages:
      * Not officially supported.  If the package is released
        publicly, then it must be tested with each major version.
      * Sometimes overly complicated.
      * Definitely requires extension to be GPLv2+.

  hglib:
    Advantages:
      * API claimed to be stable.  Hopefully this means we don't need
        to test against every version.
      * Released under MIT license.  In principle this gives more
        flexibility, but in practice it might not help much since one
        needs to use a portion of the Mercurial API to define the
        extension anyway.
      * Quite simple interface.
    Disadvantages:
      * Requires an extra install.  (Not a bit deal - it pip installs
        quite nicely.)
      * Slower (not much though 12s instead of 10s for test suite)
      * Cannot be used to define extensions on its own.
"""
from contextlib import contextmanager
import os
import sys
import functools
import shlex

import hglib

from mercurial.dispatch import dispatch, request
from mercurial import cmdutil, commands, hook
from mercurial.i18n import _    # International support

import nbstripout

cmdtable = {}
command = cmdutil.command(cmdtable)

testedwith = '3.6.3'


######################################################################
# Helpers
_COMMANDS = []


API = False


class NBClean(object):
    """Class to encapsulate the commands.

    The initial goal here is to provide a simple way to do the
    following:

    * Write functions using the mercurial command-line syntax. This is
      done by using mercurial.dispatch, and shlex.strip to convert
      commands into a simple format.
    * Suppress output in an easy way.

    """
    def __init__(self):
        self.ui = None
        self.repo = None
        self.client = None
        self.devnull = open(os.devnull, 'w')

        # The following tags/branch names are used:
        _tags = [
            'checkpoint',  # This is a checkpoint of the initial
                           # working copy with all output etc.  After
                           # any operation this state of the working
                           # copy should be restored.
            'parent',  # This points to the revision that is/should be
                       # the parent of the working copy.  If commits
                       # are made, it will be updated.
            'new',  # If a new commit is required for the checkpoint,
                    # then this will refer to it.  It should
                    # ultimately be striped.
            ]
        _prefix = '_nbclean'

        self.tags = dict((_t, '_'.join([_prefix, _t])) for _t in _tags)

        # Register commands with mercurial
        for name, opts, synopsis in _COMMANDS:
            command(name, opts, synopsis)(getattr(self, name))

    def __del__(self):
        self.devnull.close()

    def dispatch(self, cmd, fout=None, ferr=None):
        """Wrapper to run a command and deal with output."""
        # Note: There are two ways to interact with mercurial.  The most
        # stable is with the command lined interface which can be accesed
        # using dispatch(requst(commandline)) as mentioned here:
        # http://stackoverflow.com/a/8972531/1088938
        #
        # Here are some notes about these:
        #
        # request(args, ui=None, repo=None, fin=None, fout=None, ferr=None)
        # dispatch(req)
        #
        # Dispatch returns:
        # -1: Abort was raised or ParseError.
        if API:
            if ferr is False:
                ferr = self.devnull
            if fout is False:
                fout = self.devnull

            if isinstance(cmd, str):
                cmd = shlex.split(cmd)

            self.cmd = cmd
            self.req = request(cmd, fout=fout, ferr=ferr)
            self.result = dispatch(self.req)

        else:
            from hglib.util import b, BytesIO

            out, err = BytesIO(), BytesIO()
            outchannels = {b('o'): out.write, b('e'): err.write}

            inchannels = {}
            if isinstance(cmd, str):
                cmd = shlex.split(cmd)
            cmd = map(b, cmd)
            self.result = self.client.runcommand(
                cmd, inchannels, outchannels)
            if fout is None:
                self.ui.status(out.getvalue())
            if ferr is None:
                self.ui.warn(err.getvalue())

        # result is an errorcode.  We negate it to return a boolean
        # indicating if the command succeded
        return not self.result

    def _cmd(opts=[], synopsis=_('')):
        """Decorator like command that uses the function name and sets
        self.ui, self.repo, and self.client."""
        def wrap(f):
            @functools.wraps(f)
            def wrapper(self, ui=None, repo=None, **kw):
                if ui is not None:
                    self.ui = ui
                if repo is not None:
                    self.repo = repo
                if not self.client and not API:
                    self.client = hglib.open(self.repo.pathto(''))
                return f(self, **kw)

            name = f.func_name
            _COMMANDS.append((name, opts, synopsis))
            return wrapper
        return wrap

    ######################################################################
    # Internal Commands
    #
    # These are shortcuts for the commands we use.  They are not
    # exposed to the user.  The default values are different from the
    # usual versions of the commands so that the main part of our code
    # is cleaner.
    def msg(self, msg, err=False):
        if API:
            msg = _(msg)        # Internationalization
        msg = msg + "\n"

        if err:
            self.ui.warn(msg)
        else:
            self.ui.status(msg)

    def isquiet(self):
        """Return True if the user has specified the global -q flag."""
        return self.config('quiet', section='ui')

    def isclean(self):
        """Return True if the repository is clean.

        Replaces the shell command::

            hg summary | grep -q 'commit: (clean)'
        """
        if API:
            ctx = self.repo[None]
            subs = [s for s in ctx.substate if ctx.sub(s).dirty()]
            status = self.repo.status()
            return not (status.modified or status.added or status.removed
                        or subs or self.repo.dirstate.copies())
        else:
            return self.client.summary()['commit']

    def setparent(self, parent, ferr=None):
        """Set the parent node without changing the working copy.

        This is something like calling update followed by revert.
        """""
        self.dispatch('debugsetparents "{}"'.format(parent), ferr=ferr)
        self.dispatch('debugrebuilddirstate', ferr=ferr)

    def bookmark(self, name, inactive=True, delete=False):
        """We use inactive bookmarks by default so they act like tags
        and do not advance.
        """
        if API:
            opts = []
            if delete:
                opts.append('--delete')
            elif inactive:
                opts.append('-i')
            self.dispatch('bookmarks {} {}'.format(' '.join(opts), name))
        else:
            self.client.bookmark(name, inactive=inactive, delete=delete)

    def strip(self, name, nobackup=True, ferr=False):
        """Force strip a changeset without a backup and suppressing
        the error messages."""
        opts = []
        if nobackup:
            opts.append('--no-backup')
        self.dispatch('strip {} {}'.format(name, ' '.join(opts)), ferr=False)

    def revert(self, rev, files=(), all=True, nobackup=True):
        """Revert all files to the specified revision without backup
        files (.orig) and without any messages."""
        if API:
            opts = ['-q']
            if all:
                opts.append('--all')
            if nobackup:
                opts.append('-C')
            return self.dispatch('revert {} -r {} {}'.format(
                ' '.join(opts), rev, ' '.join(files)))
        else:
            files = list(files)
            return not self.client.revert(
                files, rev=rev, all=all, nobackup=nobackup)

    def update(self, rev, clean=True):
        """Update (clean by default) quietly"""
        if True or API:
            opts = ['-q']
            if clean:
                opts.append('-C')
            return self.dispatch('update {} {}'
                                 .format(' '.join(opts), rev),
                                 ferr=False)
        else:
            try:
                result = not self.client.update(rev, clean=clean)
            except hglib.error.CommandError:
                result = False
            return result

    def branch(self, name):
        """Create branch"""
        if not self.isquiet():
            self.msg("marked working directory as branch {}".format(name))

        if API:
            with self.suppress_output:
                return self.dispatch('branch -q "{}"'.format(name))
        else:
            self.client.branch(name)

    def checkpoint(self):
        """Create a checkpoint of the current working copy.

        See also:
            hg nbrestore
        """
        # Preconditions
        #   * None
        # Postconditions
        #   * The current working copy is stored in a node with
        #     bookmark 'checkpoint'
        #   * If a new node was created to do this, it has tag 'new'
        self.bookmark(self.tags['parent'])
        if API:
            if self.dispatch('commit -qm "CHK: auto checkpoint"'):
                self.dispatch('tag -fl {}'.format(self.tags['new']))
        else:
            try:
                self.client.commit(message="CHK: auto checkpoint")
                self.client.tag(names=self.tags['new'], local=True, force=True)
            except hglib.error.CommandError:
                pass
        self.bookmark(self.tags['checkpoint'])

    @property
    @contextmanager
    def suppress_output(self):
        """Context to suppress output"""
        _q = self.ui.quiet
        self.ui.quiet = True
        yield
        self.ui.quiet = _q

    def quiet_commit(self, message):
        """Helper function that does a quiet commit without hooks"""
        # For some reason, global options like quiet=True
        # cannot be passed through the commands.commit
        # interface.  We could call self.dispatch('_commit') as an
        # alias here but not self.dispatch('commit') since the latter
        # might call hooks.  We do this so we do not need an alias.
        with self.suppress_output:
            res = commands.commit(self.ui, self.repo, message=message)
        return not res

    def automerge(self, src, dest, checkpoint):
        """Merges revision src onto dest keeping working copy exactly
        as in checkpoint.

        Equivalent to (modulo message suppression etc.)::

            hg update checkpoint
            hg update dest
            hg merge src
            hg revert --all checkpoint
        """
        # Makes sure any files are added then removed properly
        self.update(checkpoint)
        self.update(dest)
        if API:
            self.dispatch('merge -q {} --tool :other'.format(src), ferr=False)
        else:
            self.client.merge(rev=src, tool=":other")

        # We do this twice because of bug 5052:
        # https://bz.mercurial-scm.org/show_bug.cgi?id=5052
        self.revert(checkpoint)
        self.revert(checkpoint)

    def config(self, name,  default='', section='nbclean'):
        """Return the value of nbclean.name from the configuration
        file."""
        if API:
            return self.ui.config(section, name, default=default)
        else:
            res = dict((_key, _value)
                       for _section, _key, _value
                       in self.client.config('nbclean'))
            return res.get(name, default)

    @_cmd()
    def nbrestore(self):
        """Restore a repository from a checkpoint.

        See also:
           hg checkpoint
        """
        # Preconditions
        #   * Working copy stored in a node with tag 'checkpoint'
        #   * This might be a new node with tag 'new'
        # Postconditions
        #   * Working copy restored to state in 'checkpoint'
        #   * If there was a node with tag 'new', it is stripped
        #   * Both tags 'checkpoint' and 'new' are removed
        self.msg("restoring output")
        self.update(self.tags['parent'])
        self.revert(self.tags['checkpoint'])
        self.strip(self.tags['new'])
        self.bookmark(self.tags['parent'], delete=True)
        self.bookmark(self.tags['checkpoint'], delete=True)

    @_cmd()
    def nbclean(self):
        """Clean output from all added or modified .ipynb notebooks.

        See also:
           hg nbrestore
        """
        # Preconditions
        #   * Nothing - this is an entrypoint.
        # Postconditions
        #   EITHER
        #     * raise Abort with no change
        #   OR
        #     * Current state checkpointed in revision with tag 'checkpoint'
        #     * Potentially new checkpoint commit with tag 'checkpoint'
        #     * All A or M .ipynb have output stripped
        #     * Desired parent node has tag 'parent'.  (This might
        #       be the original parent, or might be a new commit.)

        self.msg("cleaning output")
        self.checkpoint()
        self.update(self.tags['parent'])
        self.revert(self.tags['checkpoint'])

        # hg status -man0 | xargs -0 nbstripout
        status = self.repo.status()
        filenames = status.modified + status.added
        notebooks = [_f for _f in filenames if _f.endswith('.ipynb')]
        if notebooks:
            _argv = sys.argv
            sys.argv = ['nbstripout'] + notebooks
            nbstripout.main()
            sys.argv = _argv
        return True

    def commit_output(self, branch):
        """Commit the output to the specified branch."""
        if not branch:
            branch = self.config('output_branch')
        if branch:
            self.bookmark(self.tags['parent'])
            self.revert(self.tags['checkpoint'])
            if self.isclean():
                self.msg("no output to commit")
            else:
                if self.update(branch):
                    # Before merging, check if there are differences!
                    self.revert(self.tags['checkpoint'])
                    if not self.isclean():
                        # Only merge if there are changes!
                        self.automerge(src=self.tags['parent'],
                                       dest=branch,
                                       checkpoint=self.tags['checkpoint'])
                        self.msg("automatic commit of output")
                        self.quiet_commit(
                            "...: Automatic commit with .ipynb output")
                else:
                    # No auto_output branch exists yet.
                    self.setparent('c_parent', ferr=False)
                    self.branch(branch)
                    self.msg("automatic commit of output")
                    self.quiet_commit(
                        "...: Automatic commit with .ipynb output")
        else:
            self.bookmark(self.tags['parent'])
            self.revert(self.tags['checkpoint'])
            self.revert(self.tags['checkpoint'])

            if self.quiet_commit(
                    "...: Automatic commit with .ipynb output"):
                self.msg("automatic commit of output")
            else:
                self.msg("no output to commit")

    ######################################################################
    # External Interface
    #
    # These commands are provided by the extension

    # Get standard commit options from commands.table
    @_cmd(opts=commands.table['^commit|ci'][1]
          + [('b', 'branch', '',
              _('commit output to this branch (create if needed)'))],
          synopsis=commands.table['^commit|ci'][2])
    def ccommit(self, branch, *pats, **opts):
        self.nbclean()
        isclean = self.isclean()
        if isclean:
            self.msg("nothing changed")
        else:
            fullargs = sys.argv[1:]   # This is a guess...
            hook.hook(self.ui, self.repo, "pre-commit", True,
                      args=" ".join(fullargs),
                      pats=pats, opts=opts)
            ret = commands.commit(self.ui, self.repo, *pats, **opts)
            # run post-hook, passing command result
            hook.hook(self.ui, self.repo, "post-commit", False,
                      args=" ".join(fullargs),
                      result=ret, pats=pats, opts=opts)

            isclean = (ret is None)

        if isclean:
            self.commit_output(branch)

        self.nbrestore()

    @_cmd(opts=[
        ('b', 'branch', '',
         _('commit output to this branch (create if needed)'))])
    def crecord(self, branch, *pats, **opts):
        self.nbclean()
        isclean = self.isclean()
        if isclean:
            self.msg("nothing changed")
        else:
            self.dispatch('record')

        self.nbrestore()

    # Get standard status options from commands.table
    @_cmd(opts=commands.table['^status|st'][1],
          synopsis=commands.table['^status|st'][2])
    def cstatus(self, *pats, **opts):
        if self.nbclean():
            fullargs = sys.argv[1:]   # This is a guess...
            hook.hook(self.ui, self.repo, "pre-status", True,
                      args=" ".join(fullargs),
                      pats=pats, opts=opts)
            ret = commands.status(self.ui, self.repo, *pats, **opts)
            # run post-hook, passing command result
            hook.hook(self.ui, self.repo, "post-status", False,
                      args=" ".join(fullargs),
                      result=ret, pats=pats, opts=opts)
            self.nbrestore()

    # Get standard diff options from commands.table
    @_cmd(opts=commands.table['^diff'][1],
          synopsis=commands.table['^diff'][2])
    def cdiff(self, *pats, **opts):
        if self.nbclean():
            fullargs = sys.argv[1:]   # This is a guess...
            hook.hook(self.ui, self.repo, "pre-diff", True,
                      args=" ".join(fullargs),
                      pats=pats, opts=opts)
            ret = commands.diff(self.ui, self.repo, *pats, **opts)
            # run post-hook, passing command result
            hook.hook(self.ui, self.repo, "post-diff", False,
                      args=" ".join(fullargs),
                      result=ret, pats=pats, opts=opts)
            self.nbrestore()

_nbclean = NBClean()
