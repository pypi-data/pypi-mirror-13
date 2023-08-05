#!/bin/env python
from optparse import OptionParser
from os.path import exists

import mmf_setup

VARIABLES = [
    ('MMF_SETUP', mmf_setup.MMF_SETUP, mmf_setup.MMF_SETUP),
    ('HGRCPATH', '${{HGRCPATH}}:{HGRC}'.format(
        HGRC=mmf_setup.HGRC), mmf_setup.HGRC),
]


def run(debug=False):
    environment_string = []
    for var, val, filename in VARIABLES:
        if debug:
            print("# processing {}={} for file '{}'"
                  .format(var, val, filename))
        if not filename or exists(filename):
            environment_string.append(
                'export {var}="{val}"'.format(var=var, val=val))
        if debug and filename and not exists(filename):
            print("# processing {} failed:\n   no file '{}'"
                  .format(var, filename))
    environment_string = "\n".join(environment_string)
    print(environment_string)

parser = OptionParser()
parser.add_option("-d", "--debug",
                  action="store_true", dest="debug", default=False,
                  help="show debugging information")

if __name__ == '__main__':
    (options, args) = parser.parse_args()
    run(options.debug)
