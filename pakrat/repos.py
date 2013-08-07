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

import os
import yum
from pakrat import util, log

def from_file(path):
    """ Read repository configuration from a YUM config file.

    Using the YUM client library, read in a configuration file and return
    a list of repository objects.
    """
    if not os.path.exists(path):
        raise Exception('No such file or directory: %s' % path)
    yb = util.get_yum()
    yb.getReposFromConfigFile(path)
    for repo in yb.repos.findRepos('*'):
        yb.doSackSetup(thisrepo=repo.getAttribute('name'))
    repos = []
    for repo in yb.repos.findRepos('*'):
        if repo.isEnabled():
            log.info('Added repo %s from file %s' % (repo.id, path))
            repos.append(repo)
        else:
            log.debug('Not adding repo %s because it is disabled' % repo.id)
    return repos

def from_dir(path):
    """ Read repository configuration from a directory containing YUM configs.

    This method will look through a directory for YUM repository configuration
    files (*.repo) and read them in using the from_file method.
    """
    repos = []
    if os.path.isdir(path):
        for _file in sorted(os.listdir(path)):
            _file = os.path.join(path, _file)
            if not _file.endswith('.repo'):
                continue
            repos += from_file(_file)
    return repos
