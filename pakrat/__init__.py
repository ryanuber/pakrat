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
from pakrat import util, log, repo, repos, progress

__version__ = '0.2.5'

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

    if repoversion:
        delete = False  # versioned repos have nothing to delete

    for _file in repofiles:
        objrepos += repos.from_file(_file)

    for _dir in repodirs:
        objrepos += repos.from_dir(_dir)

    prog = progress.Progress()

    manager = multiprocessing.Manager()
    queue = manager.Queue()
    processes = []
    for objrepo in objrepos:
        prog.update(objrepo.id)
        yumcallback = progress.YumProgress(objrepo.id, queue)
        callback = progress.ProgressCallback(objrepo.id, queue)
        dest = util.get_repo_dir(basedir, objrepo.id)
        p = multiprocessing.Process(target=repo.sync, args=(objrepo, dest,
                                    repoversion, delete, yumcallback,
                                    callback))
        p.start()
        processes.append(p)

    def stop(*args):
        """ Inner method for terminating threads on signal events.

        This method uses os.kill() to send a SIGKILL directly to the process ID
        because the child processes are running blocking calls that will likely
        take a long time to complete.
        """
        log.error('Caught exit signal - aborting')
        while len(processes) > 0:
            for p in processes:
                os.kill(p.pid, signal.SIGKILL)
                if not p.is_alive():
                    processes.remove(p)
        sys.exit(1)

    # Catch user-cancelled or killed signals to terminate threads.
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    while len(processes) > 0:
        while not queue.empty():
            e = queue.get()
            if not e.has_key('action'):
                continue
            if e['action'] == 'init' and e.has_key('value'):
                prog.update(e['repo_id'], set_total=e['value'])
            elif e['action'] == 'downloaded' and e.has_key('value'):
                prog.update(e['repo_id'], add_downloaded=e['value'])
            elif e['action'] == 'dlcomplete':
                prog.update(e['repo_id'], set_dlcomplete=True)
            elif e['action'] == 'mdworking':
                prog.update(e['repo_id'], set_repomd='working')
            elif e['action'] == 'mdcomplete':
                prog.update(e['repo_id'], set_repomd='complete')
        for p in processes:
            if not p.is_alive():
                processes.remove(p)

    #prog.complete_all()
