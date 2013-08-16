# pakrat - A tool for mirroring and versioning YUM repositories.
# Copyright 2013 Ryan Uber <ru@ryanuber.com>. All rights reserved.
#
# MIT LICENSE
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
import syslog

def write(pri, message):
    """ Record a log message.

    Currently just uses syslog, and if unattended, writes the log messages
    to stdout so they can be piped elsewhere.
    """
    syslog.openlog('pakrat')  # sets log ident
    syslog.syslog(pri, message)
    if not sys.stdout.isatty():
        print message  # print if running unattended

def debug(message):
    """ Record a debugging message. """
    write(syslog.LOG_DEBUG, 'debug: %s' % message)

def trace(message):
    """ Record a trace message """
    write(syslog.LOG_DEBUG, 'trace: %s' % message)

def error(message):
    """ Record an error message. """
    write(syslog.LOG_ERR, 'error: %s' % message)

def info(message):
    """ Record an informational message. """
    write(syslog.LOG_INFO, message)
