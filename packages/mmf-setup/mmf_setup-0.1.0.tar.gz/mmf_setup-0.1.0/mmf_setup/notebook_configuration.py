"""Jupyter Notebook initialization.

Usage:

1) Add the following to the first code cell of your notebook:

   import mmf_setup; mmf_setup.nbinit()

2) Execute and save the results.

3) Trust the notebook (File->Trust Notebook).


This module provides customization for Jupyter notebooks including
styling and some pre-defined MathJaX macros.
"""
__all__ = ['nbinit']

from collections import OrderedDict
import os.path
import IPython
from IPython.display import HTML, Javascript, display, clear_output
import notebook
import warnings

_HERE = os.path.abspath(os.path.dirname(__file__))


class ExtensionManager(object):
    """Manages a list of extensions."""
    _CALICO_URL = 'https://bitbucket.org/ipre/calico/downloads/'

    # Should be tuples of (name, source, [files]) where name is the
    # name of the extension, source is the URL, and [files] is a list
    # of the files installed.
    _EXTENSIONS = OrderedDict(
        [('calico-document-tools', (
            _CALICO_URL + 'calico-document-tools-1.0.zip',
            ['bibtex.js', 'calico-document-tools.js'])
          ),
         ('calico-cell-tools', (
             _CALICO_URL + 'calico-cell-tools-1.0.zip',
             ['calico-cell-tools.css', 'calico-cell-tools.js'])
          ),
         ('calico-spell-check', (
             _CALICO_URL + 'calico-spell-check-1.0.zip',
             ['calico-spell-check.css', 'calico-spell-check.js',
              'words.json', 'typo'])
          ),
         ])

    def check(self, name, verbose=False):
        """Return True if the extension is installed."""
        url, files = self._EXTENSIONS[name]
        missing = set(
            _f for _f in files
            if not notebook.nbextensions.check_nbextension(_f, user=True))
        if missing:
            for _f in missing:
                if verbose:
                    warnings.warn('Extension {} file {} missing'
                                  .format(name, _f))
            return False
        return True

    @property
    def extensions(self):
        pass

    def install(self, name, verbose=0):
        url, files = self._EXTENSIONS[name]
        if not self.check(name):
            notebook.install_nbextension(
                url, overwrite=True, user=True, verbose=verbose)

    def enable(self, name, verbose=0):
        notebook.nbextensions.EnableNBExtensionApp().enable_nbextension(name)

    def disable(self, name, verbose=0):
        notebook.nbextensions.DisableNBExtensionApp().disable_nbextension(name)

    def install_all(self, verbose=0):
        for name in self._EXTENSIONS:
            self.install(name, verbose=verbose)

    def enable_all(self):
        map(self.enable, self._EXTENSIONS)

    def disable_all(self):
        map(self.disable, self._EXTENSIONS)

    def install_all(self, verbose=0):
        for name in self._EXTENSIONS:
            self.install(name, verbose=verbose)

    def uninstall(self, name):
        """Not so hard, but not yet implemented.
        See nbextensions.py"""
        raise NotImplementedError


def install_extensions():
    em = ExtensionManager()
    em.install_all()
    em.enable_all()


def nbinit(theme='mmf', toggle_code=False):
    install_extensions(verbose=2)
    clear_output()
    with open(os.path.join(
            _HERE, 'themes', '{theme}.css'.format(theme=theme))) as _f:
        display(HTML(r"<style>{}</style>".format(_f.read())))

    with open(os.path.join(
            _HERE, 'themes', '{theme}.js'.format(theme=theme))) as _f:
        display(Javascript(_f.read()))

    with open(os.path.join(
            _HERE, 'themes', '{theme}.html'.format(theme=theme))) as _f:
        display(HTML(_f.read()))

    if toggle_code:
        display(HTML(r"""<script>
code_show=true;
function code_toggle() {
 if (code_show){
 $('div.input').hide();
 } else {
 $('div.input').show();
 }
 code_show = !code_show
}
$( document ).ready(code_toggle);
</script>
<form action="javascript:code_toggle()"><input type="submit"
    value="Click here to toggle on/off the raw code."></form>
        """))
