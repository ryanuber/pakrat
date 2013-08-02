import os
from pakrat.yumbase import yumbase
from pakrat import log

def get_yum():
    yb = yumbase()
    return yb

def get_repo_dir(basedir, name):
    return '%s/%s' % (basedir, name)

def get_packages_dir(repodir):
    return '%s/Packages' % repodir

def get_relative_packages_dir():
    return '../Packages'

def get_package_relativedir(packagename):
    return 'Packages/%s' % packagename

def get_versioned_dir(repodir, version):
    return '%s/%s' % (repodir, version)

def get_latest_symlink_path(repodir):
    return '%s/latest' % repodir

def get_package_filename(pkg):
    return '%s-%s-%s.%s.rpm' % (pkg.name, pkg.version, pkg.release, pkg.arch)

def validate_basedir(basedir):
    if type(basedir) is not str:
        raise Exception('basedir must be a string')

def validate_basedirs(basedirs):
    if type(basedirs) is not list:
        raise Exception('basedirs must be a list')
    for basedir in basedirs:
        validate_basedir(basedir)

def validate_baseurl(baseurl):
    if type(baseurl) is not str:
        raise Exception('baseurl must be a string')

def validate_baseurls(baseurls):
    if type(baseurls) is not list:
        raise Exception('baseurls must be a list')
    for baseurl in baseurls:
        validate_baseurl(baseurl)

def validate_mirrorlist(mirrorlist):
    if type(mirrorlist) is not str:
        raise Exception('mirrorlist must be a string')
    if not mirrorlist.start_with('http'):
        raise Exception('mirror lists must start with "http"')

def validate_repos(repos):
    if type(repos) is not list:
        raise Exception('repos must be a list')

def validate_repofiles(repofiles):
    if type(repofiles) is not list:
        raise Exception('repofiles must be a list')

def validate_repodirs(repodirs):
    if type(repodirs) is not list:
        raise Exception('repodirs must be a list')

def validate_arch(arch):
    if arch not in ['i386', 'i486', 'i586', 'i686', 'x86_64', 'noarch']:
        raise Exception('Invalid architecture "%s"' % arch)

def validate_arch_list(arch_list):
    if type(arch_list) is not list:
        raise Exception('architecture[s] must be a list')
    for arch in arch_list:
        validate_arch(arch)

def make_dir(dir):
    if not os.path.exists(dir):
        log.trace('Creating directory %s' % dir)
        os.makedirs(dir)

def symlink(path, target):
    if not os.path.islink(path):
        if os.path.isfile(path):
            raise Exception('%s is a file - Cannot create symlink' % path)
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            make_dir(dir)
    elif os.readlink(path) != target:
        log.trace('Unlinking %s because it is outdated' % path)
        os.unlink(path)
    if not os.path.lexists(path):
        log.trace('Linking %s to %s' % (path, target))
        os.symlink(target, path)
