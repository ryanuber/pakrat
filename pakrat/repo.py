import os
import sys
import tempfile
import shutil
import yum
import createrepo
import copy
from contextlib import contextmanager
from pakrat import util, log

def factory(name, baseurls=None, mirrorlist=None):
    """ Generate a pakrat.yumbase.YumBase object on-the-fly.

    This makes it possible to mirror YUM repositories without having any stored
    configuration anywhere. Simply pass in the name of the repository, and
    either one or more baseurl's or a mirrorlist URL, and you will get an
    object in return that you can pass to a mirroring function.
    """
    yb = util.get_yum()
    if baseurls is not None:
        util.validate_baseurls(baseurls)
        repo = yb.add_enable_repo(name, baseurls=baseurls)
    elif mirrorlist is not None:
        util.validate_mirrorlist(mirrorlist)
        repo = yb.add_enable_repo(name, mirrorlist=mirrorlist)
    else:
        raise Exception('One or more baseurls or mirrorlist required')
    return repo

def set_path(repo, path):
    """ Set the local filesystem path to use for a repository object. """
    util.validate_repo(repo)
    result = copy.copy(repo)  # make a copy so the original is untouched

    # The following is wrapped in a try-except to suppress an anticipated
    # exception from YUM's yumRepo.py, line 530 and 557.
    try: result.pkgdir = path
    except yum.Errors.RepoError: pass

    return result

def create_metadata(repo, sumtype, packages=None, comps=None):
    """ Generate YUM metadata for a repository.

    This method accepts a repository object and, based on its configuration,
    generates YUM metadata for it using the createrepo sister library.
    """
    util.validate_repo(repo)
    util.validate_sumtype(sumtype)
    conf = createrepo.MetaDataConfig()
    conf.directory = os.path.dirname(repo.pkgdir)
    conf.outputdir = os.path.dirname(repo.pkgdir)
    conf.sumtype = sumtype
    if packages:
        conf.pkglist = packages
    conf.quiet = True

    if comps:
        groupdir = tempfile.mkdtemp()
        conf.groupfile = os.path.join(groupdir, 'groups.xml')
        with open(conf.groupfile, 'w') as f:
            f.write(comps)

    generator = createrepo.SplitMetaDataGenerator(conf)
    generator.doPkgMetadata()
    generator.doRepoMetadata()
    generator.doFinalMove()

    if comps and os.path.exists(groupdir):
        shutil.rmtree(groupdir)

def create_combined_metadata(repo, sumtype, dest, comps=None):
    """ Creates YUM metadata for the entire Packages directory.

    When used with versioning, this creates a combined repository of all
    packages ever synced for the repository.
    """
    combined_repo = set_path(repo, util.get_packages_dir(dest))
    create_metadata(combined_repo, sumtype, None, comps)

def retrieve_group_comps(repo):
    """ Retrieve group comps XML data from a remote repository.

    This data can be used while running createrepo to provide package groups
    data that clients can use while installing software.
    """
    if repo.enablegroups:
        try:
            yb = util.get_yum()
            yb.repos.add(repo)
            comps = yb._getGroups().xml()
            log.info('Group data retrieved for repository %s' % repo.id)
            return comps
        except yum.Errors.GroupsError:
            log.debug('No group data available for repository %s' % repo.id)
            return None

def sync(repo, dest, version, delete=False, combined=False, yumcallback=None,
    repocallback=None, sumtype='sha1'):
    """ Sync repository contents from a remote source.

    Accepts a repository, destination path, and an optional version, and uses
    the YUM client library to download all available packages from the mirror.
    If the delete flag is passed, any packages found on the local filesystem
    which are not present in the remote repository will be deleted.
    """
    util.make_dir(util.get_packages_dir(dest))  # Make package storage dir

    @contextmanager
    def suppress():
        """ Suppress stdout within a context.

        This is necessary in this use case because, unfortunately, the YUM
        library will do direct printing to stdout in many error conditions.
        Since we are maintaining a real-time, in-place updating presentation
        of progress, we must suppress this, as we receive exceptions for our
        reporting purposes anyways.
        """
        stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        yield
        sys.stdout = stdout

    if version:
        dest_dir = util.get_versioned_dir(dest, version)
        util.make_dir(dest_dir)
        packages_dir = util.get_packages_dir(dest_dir)
        util.symlink(packages_dir, util.get_relative_packages_dir())
    else:
        dest_dir = dest
        packages_dir = util.get_packages_dir(dest_dir)
    try:
        yb = util.get_yum()
        repo = set_path(repo, packages_dir)
        if yumcallback:
            repo.setCallback(yumcallback)
        yb.repos.add(repo)
        yb.repos.enableRepo(repo.id)
        with suppress():
            # showdups allows us to get multiple versions of the same package.
            ygh = yb.doPackageLists(showdups=True)

        # reinstall_available = Available packages which are installed.
        packages = ygh.available + ygh.reinstall_available

        # Inform about number of packages total in the repo.
        callback(repocallback, repo, 'repo_init', len(packages))

        # Check if the packages are already downloaded. This is probably a bit
        # expensive, but the alternative is simply not knowing, which is
        # horrible for progress indication.
        for po in packages:
            local = po.localPkg()
            if os.path.exists(local):
                if yb.verifyPkg(local, po, False):
                    callback(repocallback, repo, 'local_pkg_exists',
                             util.get_package_filename(po))

        with suppress():
            yb.downloadPkgs(packages)

    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception, e:
        callback(repocallback, repo, 'repo_error', str(e))
        log.error(str(e))
        return False
    callback(repocallback, repo, 'repo_complete')

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

    log.info('Creating metadata for repository %s' % repo.id)
    callback(repocallback, repo, 'repo_metadata', 'working')
    comps = retrieve_group_comps(repo)  # try group data
    pkglist = []
    for pkg in packages:
        pkglist.append(
            util.get_package_relativedir(util.get_package_filename(pkg))
        )

    create_metadata(repo, sumtype, pkglist, comps)
    if combined and version:
        create_combined_metadata(repo, sumtype, dest, comps)
    elif os.path.exists(util.get_metadata_dir(dest)):
        # At this point the combined metadata is stale, so remove it.
        log.debug('Removing combined metadata for repository %s' % repo.id)
        shutil.rmtree(util.get_metadata_dir(dest))
    callback(repocallback, repo, 'repo_metadata', 'complete')
    log.info('Finished creating metadata for repository %s' % repo.id)

    if version:
        latest_symlink = util.get_latest_symlink_path(dest)
        util.symlink(latest_symlink, version)

def callback(callback_obj, repo, event, data=None):
    """ Abstracts calling class callbacks.

    Since callbacks are optional, a function should check if the callback is
    set or not, and then call it, so we don't repeat this code many times.
    """
    if callback_obj and hasattr(callback_obj, event):
        method = getattr(callback_obj, event)
        if data:
            method(repo.id, data)
        else:
            method(repo.id)
