import os
from datetime import datetime
from pakrat.yumbase import yumbase

def get_yum():
    yb = yumbase()
    return yb

def get_repo_version():
    now = datetime.now()
    return '%s-%s-%s' % (now.month, now.day, now.year)

def get_repo_dir(basedir, name):
    return '%s/%s' % (basedir, name)

def get_packages_dir(repodir):
    return '%s/packages' % repodir

def get_versioned_dir(repodir, version):
    return '%s/%s' % (repodir, version)

def get_latest_symlink_path(repodir):
    return '%s/latest' % repodir

def get_package_symlink_path(versioned_dir, pkg_file):
    return '%s/%s' % (versioned_dir, pkg_file)

def get_package_symlink_target(pkg_file):
    return '../packages/%s' % pkg_file

def get_package_filename(pkg):
    return '%s-%s-%s.%s.rpm' % (pkg.name, pkg.version, pkg.release, pkg.arch)

def validate_basedir(basedir):
    if type(basedir) is not str:
        raise pakrat.exception('basedir must be a string')

def validate_basedirs(basedirs):
    if type(basedirs) is not list:
        raise pakrat.exception('basedirs must be a list')
    for basedir in basedirs:
        validate_basedir(basedir)

def validate_baseurl(baseurl):
    if type(baseurl) is not str:
        raise pakrat.exception('baseurl must be a string')

def validate_baseurls(baseurls):
    if type(baseurls) is not list:
        raise pakrat.exception('baseurls must be a list')
    for baseurl in baseurls:
        validate_baseurl(baseurl)

def validate_mirrorlist(mirrorlist):
    if type(mirrorlist) is not str:
        raise pakrat.exception('mirrorlist must be a string')
    if not mirrorlist.start_with('http'):
        raise pakrat.exception('mirror lists must start with "http"')

def validate_repos(repos):
    if type(repos) is not list:
        raise pakrat.exception('repos must be a list')

def validate_repofiles(repofiles):
    if type(repofiles) is not list:
        raise pakrat.exception('repofiles must be a list')

def validate_repodirs(repodirs):
    if type(repodirs) is not list:
        raise pakrat.exception('repodirs must be a list')

def validate_arch(arch):
    if arch not in ['i386', 'i486', 'i586', 'i686', 'x86_64', 'noarch']:
        raise pakrat.exception('Invalid architecture "%s"' % arch)

def validate_arch_list(arch_list):
    if type(arch_list) is not list:
        raise pakrat.exception('architecture[s] must be a list')
    for arch in arch_list:
        validate_arch(arch)

def make_dir(dir):
    if not os.path.exists(dir):
        Log.debug('Creating directory %s' % dir)
        os.makedirs(dir)

def symlink(path, target):
    if not os.path.islink(path):
        if os.path.isfile(path):
            raise pakrat.exception('%s is a file - Cannot create symlink' % path)
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            make_dir(dir)
    elif os.readlink(path) != target:
        Log.debug('Unlinking %s because it is outdated' % path)
        os.unlink(path)
    if not os.path.lexists(path):
        Log.debug('Linking %s to %s' % (path, target))
        os.symlink(target, path)
