import os
import sys
import multiprocessing
import subprocess
import signal
import urlparse
from yum.Errors import RepoError
from pakrat import util, log, repotools

__version__ = '0.0.7'

def sync(basedir, repos=[], repodirs=[], repofiles=[], repoversion=None, delete=False):
    util.validate_basedir(basedir)
    util.validate_repos(repos)
    util.validate_repofiles(repofiles)
    util.validate_repodirs(repodirs)
    util.validate_repos(repos)

    if repoversion:
        delete = False

    for file in repofiles:
        for filerepo in repotools.from_file(file):
            repos.append(filerepo)

    for dir in repodirs:
        for dirrepo in repotools.from_dir(dir):
            repos.append(dirrepo)

    processes = []
    for repo in repos:
        dest = util.get_repo_dir(basedir, repo.id)
        p = multiprocessing.Process(target=sync_repo, args=(repo, dest, repoversion, delete))
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

def sync_repo(repo, dest, version, delete=False):
    try:
        packages_dir = util.get_packages_dir(dest)
        yb = util.get_yum()
        repo = repotools.set_path(repo, packages_dir)
        yb.repos.add(repo)
        yb.repos.enableRepo(repo.id)
        ygh = yb.doPackageLists(showdups=True)
        packages = ygh.available + ygh.reinstall_available
    except RepoError, e:
        log.error(e)
        return False

    dest_dir = util.get_versioned_dir(dest, version) if version else dest
    util.make_dir(dest_dir)

    log.info('Syncing %d packages from repository %s' % (len(packages), repo.id))
    yb.downloadPkgs(packages)
    if delete:
        package_names = []
        for package in packages:
            package_names.append(util.get_package_filename(package))
        for _file in os.listdir(util.get_packages_dir(dest)):
            if not _file in package_names:
                package_path = util.get_package_path(dest, _file)
                log.debug('Deleting file %s' % package_path)
                os.remove(package_path)
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
