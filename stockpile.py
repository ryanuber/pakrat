import os
import sys
import yum
import glob
from datetime import datetime

class StockpileYumBase(yum.YumBase):

    def __init__(self):
        yum.YumBase.__init__(self)
        self.preconf = yum._YumPreBaseConf()
        self.preconf.debuglevel = 0
        self.setCacheDir(force=True, reuse=False, tmpdir=yum.misc.getCacheDir())
        self.repos.repos = {}

class Stockpile:

    class Log:

        @staticmethod
        def write(message):
            print message

        @staticmethod
        def debug(message):
            Stockpile.Log.write('debug: %s' % message)

        @staticmethod
        def info(message):
            Stockpile.Log.write('info: %s' % message)

    @staticmethod
    def get_yum():
        yb = StockpileYumBase()
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
            Stockpile.Log.debug('Creating directory %s' % dir)
            os.makedirs(dir)

    @staticmethod
    def symlink(path, target):
        if not os.path.islink(path):
            if os.path.isfile(path):
                raise StockpileException('%s is a file - Cannot create symlink' % path)
            dir = os.path.dirname(path)
            if not os.path.exists(dir):
                Stockpile.make_dir(dir)
        elif os.readlink(path) != target:
            Stockpile.Log.debug('Unlinking %s because it is outdated' % path)
            os.unlink(path)
        if not os.path.lexists(path):
            Stockpile.Log.debug('Linking %s to %s' % (path, target))
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
    def sync(basedir, repos=[], repofiles=[], repodirs=[]):
        if type(basedir) is not str:
            raise StockpileException('Basedir must be a string')
        if type(repos) is not list:
            raise StockpileException('Repos must be a list')
        if type(repofiles) is not list:
            raise StockpileException('Repo files must be passed as a list')
        if type(repodirs) is not list:
            raise StockpileException('Repo dirs must be passed as a list')

        for file in repofiles:
            for filerepo in Stockpile.repos_from_file(file):
                repos.append(filerepo)

        for dir in repodirs:
            for dirrepo in Stockpile.repos_from_dir(dir):
                repos.append(dirrepo)

        repo_version = Stockpile.get_repo_version()

        for repo in repos:
            yb = Stockpile.get_yum()
            yb.repos.repos[repo.name] = repo

            repo_dir = Stockpile.get_repo_dir(basedir, repo.id)
            packages_dir = Stockpile.get_packages_dir(repo_dir)
            versioned_dir = Stockpile.get_versioned_dir(repo_dir, repo_version)
            latest_symlink = Stockpile.get_latest_symlink_path(repo_dir)

            repo = Stockpile.set_repo_path(repo, packages_dir)

            packages = yb.doPackageLists(pkgnarrow='available', showdups=False)
            Stockpile.Log.info('Downloading packages from repository %s' % repo.id)
            yb.downloadPkgs(packages)
            Stockpile.Log.info('Finished downloading packages from repository %s' % repo.id)

            Stockpile.make_dir(versioned_dir)

            for pkg in packages:
                pkg_file = Stockpile.get_package_filename(pkg)
                symlink = Stockpile.get_package_symlink_path(versioned_dir, pkg_file)
                link_to = Stockpile.get_package_symlink_target(pkg_file)

                Stockpile.symlink(symlink, link_to)

            Stockpile.symlink(latest_symlink, repo_version)

    @staticmethod
    def repos_from_file(path):
        if not os.path.exists(path):
            raise StockpileException('No such file or directory: %s' % path)
        yb = Stockpile.get_yum()
        yb.getReposFromConfigFile(path)
        for repo in yb.repos.findRepos('*'):
            yb.doSackSetup(thisrepo=repo.getAttribute('name'))
        repos = []
        for repo in yb.repos.findRepos('*'):
            if repo.isEnabled():
                Stockpile.Log.info('Added repo %s from file %s' % (repo.id, path))
                repos.append(repo)
            else:
                Stockpile.Log.debug('Not adding repo %s because it is disabled' % repo.id)
        return repos

    @staticmethod
    def repos_from_dir(path):
        repos = []
        if os.path.isdir(path):
            for file in sorted(glob.glob('%s/*.repo' % path)):
                for repo in Stockpile.repos_from_file(file):
                    repos.append(repo)
        return repos


class StockpileException(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)



if __name__ == '__main__':

    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('--dest', dest='dest')
    parser.add_option('-d', '--repodir', action='append', default=[])
    parser.add_option('-f', '--repofile', action='append', default=[])
    options, args = parser.parse_args()

    if not options.dest:
        print '--dest is required'
        sys.exit(0)

    Stockpile.sync(options.dest, repofiles=options.repofile, repodirs=options.repodir)
