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
import tempfile
import shutil
import yum
import createrepo
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
    # The following is wrapped in a try-except to suppress an anticipated
    # exception from YUM's yumRepo.py, line 530 and 557.
    try: repo.pkgdir = path
    except yum.Errors.RepoError: pass
    return repo

def create_metadata(repo, packages=None, comps=None):
    """ Generate YUM metadata for a repository.

    This method accepts a repository object and, based on its configuration,
    generates YUM metadata for it using the createrepo sister library.
    """
    util.validate_repo(repo)
    conf = createrepo.MetaDataConfig()
    conf.directory = os.path.dirname(repo.pkgdir)
    conf.outputdir = os.path.dirname(repo.pkgdir)
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

def sync(repo, dest, version, delete=False, yumcallback=None,
         repocallback=None):
    """ Sync repository contents from a remote source.

    Accepts a repository, destination path, and an optional version, and uses
    the YUM client library to download all available packages from the mirror.
    If the delete flag is passed, any packages found on the local filesystem
    which are not present in the remote repository will be deleted.
    """
    util.make_dir(util.get_packages_dir(dest))  # Make package storage dir
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
        # showdups allows us to get multiple versions of the same package.
        ygh = yb.doPackageLists(showdups=True)
        packages = ygh.available + ygh.reinstall_available
    except yum.Errors.RepoError, e:
        log.error(e)
        return False

    callback(repocallback, repo, 'repo_init', len(packages))  # total repo pkgs
    yb.downloadPkgs(packages)
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

    comps = None
    if repo.enablegroups:
        try:
            comps = yb._getGroups().xml()
            log.info('Group data retrieved for repository %s' % repo.id)
        except yum.Errors.GroupsError:
            log.debug('No group data available for repository %s' % repo.id)
            pass

    log.info('Creating metadata for repository %s' % repo.id)
    pkglist = []
    for pkg in packages:
        pkglist.append(
            util.get_package_relativedir(util.get_package_filename(pkg))
        )

    # createrepo enclosed in callbacks so we know when it starts and ends
    callback(repocallback, repo, 'repo_metadata', 'working')
    create_metadata(repo, pkglist, comps)
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
