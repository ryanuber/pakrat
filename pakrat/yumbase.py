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

import yum

""" YumBase object specifically for pakrat.

This class is a simple extension of the yum.YumBase class. It is required
because pakrat uses YUM in an atypical way. When we load a YUM object, we want
only the scaffolding, and none of the system repositories or other inherited
configuration. This sounds easy but is not really built-in to YUM. This method
also uses the YUM client library to create its own cachedir on instantiation.
"""
class YumBase(yum.YumBase):

    def __init__(self):
        """ Create a new YumBase object for use in pakrat. """
        yum.YumBase.__init__(self)
        self.preconf = yum._YumPreBaseConf()
        self.preconf.debuglevel = 0
        self.prerepoconf = yum._YumPreRepoConf()
        self.setCacheDir(force=True, reuse=False,
                         tmpdir=yum.misc.getCacheDir())
        self.repos.repos = {}
