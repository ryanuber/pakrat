import os
import sys
import multiprocessing
import subprocess
import signal
import urlparse
from yum.Errors import RepoError
from pakrat import util, log, repotools

__version__ = '0.0.7'

def sync(repos=[], repoversion=None):
    util.validate_repos(repos)

    processes = []
    for repo in repos:
        dest = urlparse.urlsplit(repo.baseurl[0]).path.strip('/')
        p = multiprocessing.Process(target=sync_repo, args=(repo, dest, repoversion))
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

def sync_repo(repo, dest, version):
    try:
        packages_dir = util.get_packages_dir(dest)
        yb = util.get_yum()
        repo = repotools.set_path(repo, packages_dir)
        yb.repos.add(repo)
        yb.repos.enableRepo(repo.id)
        packages = []
        for package in yb.doPackageLists(pkgnarrow='available', showdups=False):
            packages.append(package)
    except RepoError, e:
        log.error(e)
        return False

    dest_dir = util.get_versioned_dir(dest, version) if version else dest
    util.make_dir(dest_dir)

    log.info('Syncing %d packages from repository %s' % (len(packages), repo.id))
    yb.downloadPkgs(packages)
    log.info('Finished downloading packages from repository %s' % repo.id)

    if version:
    	util.symlink(util.get_packages_dir(dest_dir), util.get_relative_packages_dir())

    log.info('Creating metadata for repository %s' % repo.id)
    pkglist = []
    for pkg in packages:
        pkglist.append(util.get_package_relativedir(util.get_package_filename(pkg)))
    repotools.create_metadata(dest_dir, pkglist)
    log.info('Finished creating metadata for repository %s' % repo.id)

    if version:
        latest_symlink = util.get_latest_symlink_path(dest)
        util.symlink(latest_symlink, version)

def repo(name, arch=None, baseurls=None, mirrorlist=None):
    yb = util.get_yum()
    if baseurls is not None:
        util.validate_baseurls(baseurls)
        repo = yb.add_enable_repo(name, baseurls=baseurls)
    if mirrorlist is not None:
        util.validate_mirrorlist(mirrorlist)
        repo = yb.add_enable_repo(name, mirrorlist=mirrorlist)
    if arch is not None:
        util.validate_arch_list(arch)
        yb.doSackSetup(thisrepo=name, archlist=arch)
    return repo
