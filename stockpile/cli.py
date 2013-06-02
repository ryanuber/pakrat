#!/usr/bin/env python -tt

import stockpile
from optparse import OptionParser

parser = OptionParser()
parser.add_option('--dest', dest='dest')
parser.add_option('-d', '--repodir', action='append', default=[])
parser.add_option('-f', '--repofile', action='append', default=[])
options, args = parser.parse_args()

if not options.dest:
    print '--dest is required'
    sys.exit(1)

stockpile.sync(options.dest, repofiles=options.repofile, repodirs=options.repodir)
