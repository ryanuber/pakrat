import os
import sys
import multiprocessing
import signal
import urlparse
from pakrat import util, log, repo, repos

__version__ = '0.2.2'

def sync(basedir, objrepos=[], repodirs=[], repofiles=[], repoversion=None, delete=False):
    util.validate_basedir(basedir)
    util.validate_repos(objrepos)
    util.validate_repofiles(repofiles)
    util.validate_repodirs(repodirs)
    util.validate_repos(objrepos)

    if repoversion:
        delete = False

    for file in repofiles:
        for filerepo in repos.from_file(file):
            objrepos.append(filerepo)

    for dir in repodirs:
        for dirrepo in repos.from_dir(dir):
            objrepos.append(dirrepo)

    processes = []
    for objrepo in objrepos:
        dest = util.get_repo_dir(basedir, objrepo.id)
        p = multiprocessing.Process(target=repo.sync, args=(objrepo, dest, repoversion, delete))
        p.start()
        processes.append(p)

    def cleanup(*args):
        for p in processes:
            os.kill(p.pid, signal.SIGKILL)
        sys.exit(1)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    complete_count = 0
    while True:
        for p in processes:
            if not p.is_alive():
                complete_count += 1
        if complete_count == len(processes):
            break
