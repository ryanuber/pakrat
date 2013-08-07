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
import sys
import multiprocessing
import signal
import urlparse
from pakrat import util, log, repo, repos

__version__ = '0.2.2'

def sync(basedir, objrepos=[], repodirs=[], repofiles=[], repoversion=None,
         delete=False):
    """ Mirror repositories with configuration data from multiple sources.

    Handles all input validation and higher-level logic before passing control
    on to threads for doing the actual syncing. One thread is created per
    repository to alleviate the impact of slow mirrors on faster ones.
    """
    util.validate_basedir(basedir)
    util.validate_repos(objrepos)
    util.validate_repofiles(repofiles)
    util.validate_repodirs(repodirs)
    util.validate_repos(objrepos)

    if repoversion:
        delete = False  # versioned repos have nothing to delete

    for file in repofiles:
        for filerepo in repos.from_file(file):
            objrepos.append(filerepo)

    for dir in repodirs:
        for dirrepo in repos.from_dir(dir):
            objrepos.append(dirrepo)

    processes = []
    for objrepo in objrepos:
        dest = util.get_repo_dir(basedir, objrepo.id)
        p = multiprocessing.Process(target=repo.sync, args=(objrepo, dest,
                                    repoversion, delete))
        p.start()
        processes.append(p)

    def cleanup(*args):
        """ Inner method for cleaning up threads. """
        for p in processes:
            os.kill(p.pid, signal.SIGKILL)
        sys.exit(1)

    # Catch user-cancelled or killed signals to clean up threads.  This doesn't
    # work great and probably needs to be replaced by some real thread pooling.
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    complete_count = 0
    while True:
        for p in processes:
            if not p.is_alive():
                complete_count += 1
        if complete_count == len(processes):
            break
