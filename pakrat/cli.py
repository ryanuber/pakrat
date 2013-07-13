#!/usr/bin/python -tt

import pakrat
import sys
from optparse import OptionParser

parser = OptionParser(version='pakrat %s' % pakrat.__version__)
parser.add_option('--dest')
parser.add_option('-d', '--repodir', action='append', default=[])
parser.add_option('-f', '--repofile', action='append', default=[])
parser.add_option('-r', '--repoversion', default=None)
options, args = parser.parse_args()

if not options.dest:
    print '--dest is required'
    sys.exit(1)

pakrat.sync(
    options.dest,
    repofiles=options.repofile,
    repodirs=options.repodir,
    repoversion=options.repoversion
)
