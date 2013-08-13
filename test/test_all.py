import os
import sys
import tempfile
import shutil
from flexmock import flexmock
from nose.tools import *

# Mock YUM module
repos = []

def reset_repos():
    global repos
    repos = []

def yumrepo(id, baseurls=[], mirrorlist=None):
    def getAttribute(attr):
        if attr == 'name':
            return id
    return flexmock(
        id=id,
        baseurls=baseurls,
        mirrorlist=mirrorlist,
        pkgdir='/pkgdir',
        getAttribute=lambda attr: getAttribute(attr),
        isEnabled=lambda: True
    )

def yumpkg(name, version, release, arch):
    return flexmock(name=name, version=version, release=release, arch=arch)

def yum_YumBase_doPackageLists(*args, **kwargs):
    return flexmock(
        available=[
            yumpkg('pakrat', '0.2.3', '1.el6', 'noarch')
        ],
        reinstall_available=[
            yumpkg('kernel', '2.6.32', '128-9.el6', 'x86_64'),
            yumpkg('grub', '0.99', '1.el6', 'x86_64')
        ]
    )

def yum_YumBase_add_enable_repo(name, baseurls=[], mirrorlist=None):
    repo = yumrepo(name, baseurls, mirrorlist)
    repos.append(repo)
    return repo

def yum_YumBase_repos_add(name, baseurls=[], mirrorlist=None):
    repos.append(yumrepo(name, baseurls, mirrorlist))
    return True

def yum_YumBase_findRepos(pattern):
    if pattern == '*':
        return repos

def yum_YumBase_getReposFromConfigFile(path):
    result = []
    if os.path.exists(path):
        for repo in open(path):
            name, url = repo.strip().split()
            repo = yumrepo(name, baseurls=[url])
            repos.append(repo)
            result.append(repo)
    return True

yum = flexmock()
yum._YumPreBaseConf = flexmock()
yum._YumPreRepoConf = flexmock()
yum.misc = flexmock(
    getCacheDir=lambda: '/tmp/pakrat'
)
yum.YumBase = flexmock(
    add_enable_repo=yum_YumBase_add_enable_repo,
    setCacheDir=lambda **kwargs: True,
    doPackageLists=yum_YumBase_doPackageLists,
    doSackSetup=lambda *args, **kwargs: True,
    downloadPkgs=lambda packages: True,
    repos=flexmock(
        repos={},
        enableRepo=lambda *args, **kwargs: True,
        add=yum_YumBase_repos_add,
        findRepos=yum_YumBase_findRepos
    ),
    getReposFromConfigFile=yum_YumBase_getReposFromConfigFile
)
yum.YumBase.repos.add = yum_YumBase_repos_add
yum.yumRepo = flexmock()
yum.yumRepo.YumRepository = flexmock(
    pkgdir='/pkgdir',
    getAttrubite=lambda: True
)
yum.Errors = flexmock()
yum.Errors.RepoError = flexmock()
sys.modules['yum'] = yum

# Mock createrepo module
createrepo = flexmock(
    SplitMetaDataGenerator=(
        lambda *args: flexmock(
            conf = {},
            doPkgMetadata=lambda: True,
            doRepoMetadata=lambda: True,
            doFinalMove=lambda: True
        )
    )
)
createrepo.MetaDataConfig = flexmock()
sys.modules['createrepo'] = createrepo

# Import pakrat after defining mocked modules
import pakrat

class test_repo_factory:

    def setUp(self):
        (flexmock(sys.modules['pakrat'])
            .should_receive('util.validate_repo')
            .and_return(True))

    def test_with_baseurl(self):
        repo = pakrat.repo.factory('repo1', baseurls=['http://url1'])
        assert_equals(repo.id, 'repo1')
        assert_equals(len(repo.baseurls), 1)
        assert_equals(repo.baseurls[0], 'http://url1')

    def test_with_multiple_baseurls(self):
        repo = pakrat.repo.factory('repo1',
            baseurls=['http://url1', 'http://url2'])
        assert_equals(len(repo.baseurls), 2)

    def test_url_types(self):
        pakrat.repo.factory('repo1',
            baseurls=['http://url1', 'https://url2', 'file:///url3'])
        assert pakrat.repo.factory('repo1', mirrorlist='http://url1')
        assert pakrat.repo.factory('repo2', mirrorlist='https://url2')

    @raises(Exception)
    def test_baseurl_exception(self):
        pakrat.repo.factory('repo1', baseurls=['http://good', 'bad'])

    @raises(Exception)
    def test_mirrorlist_exception(self):
        pakrat.repo.factory('repo1', mirrorlist='bad')

    @raises(Exception)
    def test_mirrorlist_with_file_url(self):
        pakrat.repo.factory('repo1', mirrorlist='file:///url1')

class test_set_repo_path:

    def setUp(self):
        (flexmock(sys.modules['pakrat'])
            .should_receive('util.validate_repo')
            .and_return(True))

    def test_set_repo_path(self):
        repo = pakrat.repo.factory('repo1', baseurls=['http://url1'])
        pkgdir_before = repo.pkgdir
        pakrat.repo.set_path(repo, '/newdir')
        pkgdir_after = repo.pkgdir
        assert_not_equals(pkgdir_before, pkgdir_after)
        assert_equals(pkgdir_after, '/newdir')

class test_create_metadata:

    def setUp(self):
        (flexmock(sys.modules['pakrat'])
            .should_receive('util.validate_repo')
            .and_return(True))

    def test_create_metadata(self):
        #(mocks['createrepo.SplitMetaDataGenerator']
        #    .should_receive('doPkgMetadata').times(1))
        #(mocks['createrepo.SplitMetaDataGenerator']
        #    .should_receive('doRepoMetadata').times(1))
        #(mocks['createrepo.SplitMetaDataGenerator']
        #    .should_receive('doFinalMove').times(1))
        repo = pakrat.repo.factory('repo1', baseurls=['http://url1'])
        pakrat.repo.create_metadata(repo)

class test_sync_repo:

    def setUp(self):
        self.mocks = {
            'makedirs': flexmock(sys.modules['os'],
                makedirs=lambda *args: True),
            'symlink': flexmock(sys.modules['os'],
                symlink=lambda *args, **kwargs: True)
        }
        (flexmock(sys.modules['pakrat'])
            .should_receive('util.validate_repo')
            .and_return(True))

    def test_sync_repo(self):
        (self.mocks['makedirs']
            .should_receive('makedirs')
            .with_args('/tmp/pakrat')
            .at_least.once)
        (self.mocks['makedirs']
            .should_receive('makedirs')
            .with_args('/tmp/pakrat/Packages')
            .at_least.once)
        (self.mocks['symlink']
            .should_receive('symlink')
            .times(0))
        repo = pakrat.repo.factory('repo1', baseurls=['http://url1'])
        pakrat.repo.sync(repo, '/tmp/pakrat')

    def test_sync_with_version(self):
        (self.mocks['makedirs']
            .should_receive('makedirs')
            .with_args('/tmp/pakrat/repo1')
            .at_least.once)
        (self.mocks['makedirs']
            .should_receive('makedirs')
            .with_args('/tmp/pakrat/repo1/Packages')
            .at_least.once)
        (self.mocks['makedirs']
            .should_receive('makedirs')
            .with_args('/tmp/pakrat/repo1/1.0')
            .at_least.once)
        (self.mocks['symlink']
            .should_receive('symlink')
            .with_args('../Packages', '/tmp/pakrat/repo1/1.0/Packages')
            .once)
        (self.mocks['symlink']
            .should_receive('symlink')
            .with_args('1.0', '/tmp/pakrat/repo1/latest')
            .once)
        repo = pakrat.repo.factory('repo1', baseurls=['http://url1'])
        pakrat.repo.sync(repo, '/tmp/pakrat/repo1', '1.0')

class test_repo_configs:

    def setUp(self):
        reset_repos()
        self.tempdir = tempfile.mkdtemp()
        self.repofile1 = os.path.join(self.tempdir, 'repo1.repo')
        self.repofile2 = os.path.join(self.tempdir, 'repos2and3.repo')
        self.repodir = os.path.join(self.tempdir, 'repos.d')
        self.repodir_file = os.path.join(self.repodir, 'repo4.repo')
        os.makedirs(self.repodir)
        with open(self.repofile1, 'w') as f:
            f.write('repo1 http://url1\n')
        with open(self.repofile2, 'w') as f:
            f.write('repo2 http://url2\nrepo3 http://url3\n')
        with open(self.repodir_file, 'w') as f:
            f.write('repo4 http://url4\n')

    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    def test_single_repo_from_file(self):
        repos = pakrat.repos.from_file(self.repofile1)
        assert_equals(len(repos), 1)
        assert_equals(repos[0].id, 'repo1')
        assert_equals(repos[0].baseurls, ['http://url1'])

    def test_multiple_repos_from_file(self):
        repos = pakrat.repos.from_file(self.repofile2)
        assert_equals(len(repos), 2)
        assert_equals(repos[0].id, 'repo2')
        assert_equals(repos[1].id, 'repo3')
        assert_equals(repos[0].baseurls, ['http://url2'])
        assert_equals(repos[1].baseurls, ['http://url3'])

    def test_repos_from_repo_dir(self):
        repos = pakrat.repos.from_dir(self.repodir)
        assert_equals(len(repos), 1)
        assert_equals(repos[0].id, 'repo4')
        assert_equals(repos[0].baseurls, ['http://url4'])
