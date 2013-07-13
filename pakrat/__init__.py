import multiprocessing
import subprocess
from pakrat import util, log, repotools

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

    log.info('Creating metadata for repository %s' % repo.id)
    pkglist = []
    for pkg in packages:
        pkglist.append(util.get_package_relativedir(util.get_package_filename(pkg)))
    util.symlink(util.get_packages_dir(versioned_dir), packages_dir)
    repotools.create_metadata(versioned_dir, versioned_dir, pkglist)

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
