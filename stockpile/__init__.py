import sys
import multiprocessing
import stockpile.yumbase
from stockpile import util
from stockpile import log
from stockpile import repotools

def sync(basedir, repos=[], repofiles=[], repodirs=[]):
    util.validate_basedir(basedir)
    util.validate_repos(repos)
    util.validate_repofiles(repofiles)
    util.validate_repodirs(repodirs)

    for file in repofiles:
        for filerepo in repotools.from_file(file):
            repos.append(filerepo)

    for dir in repodirs:
        for dirrepo in repotools.from_dir(dir):
            repos.append(dirrepo)

    version = util.get_repo_version()

    processes = []
    for repo in repos:
        dest = util.get_repo_dir(basedir, repo.id)
        p = multiprocessing.Process(target=sync_repo, args=(repo, dest, version))
        p.start()
        processes.append(p)

    complete_count = 0
    while True:
        for p in processes:
            if not p.is_alive():
                complete_count += 1
        if complete_count == len(processes):
            break

def sync_repo(repo, dest, version):
    yb = util.get_yum()

    packages_dir = util.get_packages_dir(dest)
    versioned_dir = util.get_versioned_dir(dest, version)
    latest_symlink = util.get_latest_symlink_path(dest)

    repo = repotools.set_path(repo, packages_dir)
    yb.repos.add(repo)
    yb.repos.enableRepo(repo.id)

    packages = []
    for package in yb.doPackageLists(pkgnarrow='available', showdups=False):
        packages.append(package)

    log.info('Syncing %d packages from repository %s' % (len(packages), repo.id))
    yb.downloadPkgs(packages)
    log.info('Finished downloading packages from repository %s' % repo.id)

    util.make_dir(versioned_dir)

    for pkg in packages:
        pkg_file = util.get_package_filename(pkg)
        symlink = util.get_package_symlink_path(versioned_dir, pkg_file)
        link_to = util.get_package_symlink_target(pkg_file)

        util.symlink(symlink, link_to)

    util.symlink(latest_symlink, version)

class exception(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
