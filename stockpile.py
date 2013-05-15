import os
import yum
from datetime import datetime

class Stockpile:

    @staticmethod
    def get_yum():
        yb = yum.YumBase()
        yb.repos.disableRepo('*')
        yb.setCacheDir(force=True, reuse=False, tmpdir=yum.misc.getCacheDir())
        return yb

    @staticmethod
    def get_repo_version():
        now = datetime.now()
        return '%s-%s-%s' % (now.month, now.day, now.year)

    @staticmethod
    def get_repo_dir(basedir, name):
        return '%s/%s' % (basedir, name)

    @staticmethod
    def get_packages_dir(repodir):
        return '%s/packages' % repodir

    @staticmethod
    def get_versioned_dir(repodir, version):
        return '%s/%s' % (repodir, version)

    @staticmethod
    def get_latest_symlink_path(repodir):
        return '%s/latest' % repodir

    @staticmethod
    def get_package_symlink_path(versioned_dir, pkg_file):
        return '%s/%s' % (versioned_dir, pkg_file)

    @staticmethod
    def get_package_symlink_target(pkg_file):
        return '../packages/%s' % pkg_file

    @staticmethod
    def get_package_filename(pkg):
        return '%s-%s-%s.%s.rpm' % (pkg.name, pkg.version, pkg.release, pkg.arch)

    @staticmethod
    def make_dir(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    @staticmethod
    def symlink(path, target):
        if not os.path.islink(path):
            if os.path.isfile(path):
                raise StockpileException('%s is a file - Cannot create symlink' % path)
            dir = os.path.basename(path)
            if not os.path.exists(dir):
                Stockpile.make_dir(dir)
        elif os.readlink(path) != target:
            os.unlink(path)
        if not os.path.exists(path):
            os.symlink(target, path)

    @staticmethod
    def repo(name, arch=None, baseurls=None, mirrorlist=None):
        yb = Stockpile.get_yum()
        if baseurls is not None:
            if type(baseurls) is not list:
                raise StockpileException('Baseurls must be passed as a list')
            repo = yb.add_enable_repo(name, baseurls=baseurls)
        if mirrorlist is not None:
            if type(mirrorlist) is not str:
                raise StockpileException('Mirrorlists must be passed as a string')
            repo = yb.add_enable_repo(name, mirrorlist=mirrorlist)
        if arch is not None:
            if type(arch) is not list:
                raise StockpileException('Arch must be passed as a list')
            yb.doSackSetup(thisrepo=name, archlist=arch)

        return repo

    @staticmethod
    def set_repo_path(repo, path):
        if type(repo) is not yum.yumRepo.YumRepository:
            raise StockpileException('Repo must be a yum.yumRepo.YumRepository instance')
        repo._dirSetAttr('pkgdir', path)
        return repo

    @staticmethod
    def sync(basedir, repos):
        if type(basedir) is not str:
            raise StockpileException('Basedir must be a string')
        if type(repos) is not list:
            raise StockpileException('Repos must be a list')

        repo_version = Stockpile.get_repo_version()

        for repo in repos:
            yb = Stockpile.get_yum()
            yb.repos.repos[repo.name] = repo

            repo_dir = Stockpile.get_repo_dir(basedir, repo.name)
            packages_dir = Stockpile.get_packages_dir(repo_dir)
            versioned_dir = Stockpile.get_versioned_dir(repo_dir, repo_version)
            latest_symlink = Stockpile.get_latest_symlink_path(repo_dir)

            repo = Stockpile.set_repo_path(repo, packages_dir)

            packages = yb.doPackageLists(pkgnarrow='available', showdups=False)
            yb.downloadPkgs(packages)

            Stockpile.make_dir(versioned_dir)

            for pkg in packages:
                pkg_file = Stockpile.get_package_filename(pkg)
                symlink = Stockpile.get_package_symlink_path(versioned_dir, pkg_file)
                link_to = Stockpile.get_package_symlink_target(pkg_file)

                Stockpile.symlink(symlink, link_to)

            Stockpile.symlink(latest_symlink, repo_version)



class StockpileException(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)



if __name__ == '__main__':
    Stockpile.sync('/root/mirrors', [
        Stockpile.repo('centos-base', ['x86_64'], ['http://mirror.centos.org/centos/6/os/x86_64']),
        Stockpile.repo('centos-updates', ['x86_64'], ['http://mirror.centos.org/centos/6/updates/x86_64']),
        Stockpile.repo('epel', ['x86_64'], ['http://dl.fedoraproject.org/pub/epel/6/x86_64'])
    ])
