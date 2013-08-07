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
import yum
import createrepo
from pakrat import util, log

def factory(name, baseurls=None, mirrorlist=None):
    """ Generate a pakrat.yumbase.YumBase object on-the-fly.

    This makes it possible to mirror YUM repositories without having any stored
    configuration anywhere. Simply pass in the name of the repository, and
    either one or more baseurl's or a mirrorlist URL, and you will get an object
    in return that you can pass to a mirroring function.
    """
    yb = util.get_yum()
    if baseurls is not None:
        util.validate_baseurls(baseurls)
        repo = yb.add_enable_repo(name, baseurls=baseurls)
    elif mirrorlist is not None:
        util.validate_mirrorlist(mirrorlist)
        repo = yb.add_enable_repo(name, mirrorlist=mirrorlist)
    else:
        raise Exception('One or more baseurls or a mirrorlist must be provided')
    return repo

def set_path(repo, path):
    """ Set the local filesystem path to use for a repository object. """
    util.validate_repo(repo)
    repo.pkgdir = path
    return repo

def create_metadata(repo, packages=None):
    """ Generate YUM metadata for a repository.

    This method accepts a repository object and, based on its configuration,
    generates YUM metadata for it using the createrepo sister library.
    """
    util.validate_repo(repo)
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
    """ Sync repository contents from a remote source.

    Accepts a repository, destination path, and an optional version, and uses
    the YUM client library to download all available packages from the mirror.
    If the delete flag is passed, any packages found on the local filesystem
    which are not present in the remote repository will be deleted.
    """
    try:
        packages_dir = util.get_packages_dir(dest)
        yb = util.get_yum()
        repo = set_path(repo, packages_dir)
        yb.repos.add(repo)
        yb.repos.enableRepo(repo.id)
        # showdups allows us to get multiple versions of the same package.
        ygh = yb.doPackageLists(showdups=True)
        packages = ygh.available + ygh.reinstall_available
    except yum.Errors.RepoError, e:
        log.error(e)
        return False

    dest_dir = util.get_versioned_dir(dest, version) if version else dest
    util.make_dir(dest_dir)

    log.info('Downloading %d packages from repository %s' % (len(packages),
             repo.id))
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
    	util.symlink(util.get_packages_dir(dest_dir),
                     util.get_relative_packages_dir())

    log.info('Creating metadata for repository %s' % repo.id)
    pkglist = []
    for pkg in packages:
        pkglist.append(util.get_package_filename(pkg))
    create_metadata(repo, pkglist)
    log.info('Finished creating metadata for repository %s' % repo.id)

    if version:
        latest_symlink = util.get_latest_symlink_path(dest)
        util.symlink(latest_symlink, version)
