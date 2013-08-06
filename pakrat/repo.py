import os
import yum
import createrepo
from pakrat import util, log

def factory(name, baseurls=None, mirrorlist=None):
    yb = util.get_yum()
    if baseurls is not None:
        util.validate_baseurls(baseurls)
        repo = yb.add_enable_repo(name, baseurls=baseurls)
    if mirrorlist is not None:
        util.validate_mirrorlist(mirrorlist)
        repo = yb.add_enable_repo(name, mirrorlist=mirrorlist)
    return repo

def set_path(repo, path):
    if type(repo) is not yum.yumRepo.YumRepository:
        raise Exception('Repo must be a yum.yumRepo.YumRepository instance')
    repo.pkgdir = path
    return repo

def create_metadata(repo, packages=None):
    conf = createrepo.MetaDataConfig()
    conf.directory = repo.pkgdir
    conf.outputdir = repo.pkgdir
    conf.pkglist = packages
    conf.quiet = True
    generator = createrepo.SplitMetaDataGenerator(conf)
    generator.doPkgMetadata()
    generator.doRepoMetadata()
    generator.doFinalMove()

def sync(repo, dest, version, delete=False):
    try:
        packages_dir = util.get_packages_dir(dest)
        yb = util.get_yum()
        repo = set_path(repo, packages_dir)
        yb.repos.add(repo)
        yb.repos.enableRepo(repo.id)
        ygh = yb.doPackageLists(showdups=True)
        packages = ygh.available + ygh.reinstall_available
    except yum.Errors.RepoError, e:
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
    create_metadata(dest_dir, pkglist)
    log.info('Finished creating metadata for repository %s' % repo.id)

    if version:
        latest_symlink = util.get_latest_symlink_path(dest)
        util.symlink(latest_symlink, version)
