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
from pakrat.yumbase import YumBase
from pakrat import log

PACKAGESDIR = 'Packages'
LATESTREPO = 'latest'

def get_yum():
    """ Retrieve a YumBase object, pre-configured. """
    return YumBase()

def get_repo_dir(basedir, name):
    """ Return the path to a repository directory.

    This is the directory in which all of the repository data will live. The
    path can be relative or fully qualified.
    """
    return os.path.join(basedir, name)

def get_packages_dir(repodir):
    """ Return the path to the packages directory of a repository. """
    return os.path.join(repodir, PACKAGESDIR)

def get_package_path(repodir, packagename):
    """ Return the path to an individual package file. """
    return os.path.join(repodir, PACKAGESDIR, packagename)

def get_relative_packages_dir():
    """ Return the relative path to the packages directory. """
    return os.path.join('..', PACKAGESDIR)

def get_package_relativedir(packagename):
    """ Return the relative path to an individual package file.

    This is used during repository metadata creation so that fragments of the
    local filesystem layout are not found in the repository index.
    """
    return os.path.join(PACKAGESDIR, packagename)

def get_versioned_dir(repodir, version):
    """ Return the path to a specific version of a repository. """
    return os.path.join(repodir, version)

def get_latest_symlink_path(repodir):
    """ Return the path to the latest repository directory.

    The latest directory will be created as a symbolic link, pointing back to
    the newest versioned copy.
    """
    return os.path.join(repodir, LATESTREPO)

def get_package_filename(pkg):
    """ From a repository object, return the name of the RPM file. """
    return '%s-%s-%s.%s.rpm' % (pkg.name, pkg.version, pkg.release, pkg.arch)

def validate_basedir(basedir):
    """ Validate the input of a basedir.

    Since a basedir can be either absolute or relative, the only thing we can
    really validate here is that the value is a regular string.
    """
    if type(basedir) is not str:
        raise Exception('basedir must be a string, not "%s"' % type(basedir))

def validate_url(url):
    """ Validate a source URL. http(s) or file-based accepted. """
    if not (url.startswith('http://') or url.startswith('https://') or
            url.startswith('file://')):
        raise Exception('Unsupported URL format "%s"' % url)

def validate_baseurl(baseurl):
    """ Validate user input of a repository baseurl. """
    if type(baseurl) is not str:
        raise Exception('baseurl must be a string')
    validate_url(baseurl)

def validate_baseurls(baseurls):
    """ Validate multiple baseurls from a list. """
    if type(baseurls) is not list:
        raise Exception('baseurls must be a list')
    for baseurl in baseurls:
        validate_baseurl(baseurl)

def validate_mirrorlist(mirrorlist):
    """ Validate a repository mirrorlist source. """
    if type(mirrorlist) is not str:
        raise Exception('mirrorlist must be a string, not "%s"' %
                        type(mirrorlist))
    if mirrorlist.startswith('file://'):
        raise Exception('mirrorlist cannot use a file:// source.')
    validate_url(mirrorlist)

def validate_repo(repo):
    """ Validate a repository object. """
    if type(repo) is not yum.yumRepo.YumRepository:
        raise Exception('repo must be a YumRepository, not "%s"' % type(repo))

def validate_repos(repos):
    """ Validate repository objects. """
    if type(repos) is not list:
        raise Exception('repos must be a list, not "%s"' % type(repos))
    for repo in repos:
        validate_repo(repo)

def validate_repofile(repofile):
    """ Validate a repository file """
    if type(repofile) is not str:
        raise Exception('repofile must be a string, not "%s"' % type(repofile))
    if not os.path.exists(repofile):
        raise Exception('repofile does not exist: "%s"' % repofile)

def validate_repofiles(repofiles):
    """ Validate paths to repofiles. """
    if type(repofiles) is not list:
        raise Exception('repofiles must be a list, not "%s"' % type(repofiles))
    for repofile in repofiles:
        validate_repofile(repofile)

def validate_repodir(repodir):
    """ Validate a repository configuration directory path """
    if type(repodir) is not str:
        raise Exception('repodir must be a string, not "%s"' % type(repodir))
    if not os.path.isdir(repodir):
        raise Exception('Path does not exist or is not a directory: "%s"' %
                        repodir)

def validate_repodirs(repodirs):
    """ Validate directories of repository files. """
    if type(repodirs) is not list:
        raise Exception('repodirs must be a list, not "%s"' % type(repodirs))
    for repodir in repodirs:
        validate_repodir(repodir)

def make_dir(dir):
    """ Create a directory recursively, if it does not exist. """
    if not os.path.exists(dir):
        log.trace('Creating directory %s' % dir)
        os.makedirs(dir)

def symlink(path, target):
    """ Create a symbolic link.

    Determines if a link in the destination already exists, and if it does,
    updates its target. If the destination exists but is not a link, throws an
    exception. If the link does not exist, it is created.
    """
    if not os.path.islink(path):
        if os.path.exists(path):
            raise Exception('%s exists - Cannot create symlink' % path)
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            make_dir(dir)
    elif os.readlink(path) != target:
        log.trace('Unlinking %s because its target is changing' % path)
        os.unlink(path)
    if not os.path.lexists(path):
        log.trace('Linking %s to %s' % (path, target))
        os.symlink(target, path)
