import sys
from flexmock import flexmock
from nose.tools import *

# Mock YUM module
yum = flexmock()
yumpkg = lambda name, version, release, arch: flexmock(
    name=name,
    version=version,
    release=release,
    arch=arch
)
yum._YumPreBaseConf = flexmock()
yum._YumPreRepoConf = flexmock()
yum.misc = flexmock(
    getCacheDir=lambda: '/tmp/pakrat'
)
yum.YumBase = flexmock(
    add_enable_repo=lambda *args, **kwargs: flexmock(
        id=args[0],
        baseurls=kwargs['baseurls'] if kwargs.has_key('baseurls') else None,
        pkgdir='/pkgdir'
    ),
    setCacheDir=lambda **kwargs: True,
    doPackageLists=lambda *args, **kwargs: flexmock(
        available=[
            yumpkg('pakrat', '0.2.3', '1.el6', 'noarch')
        ],
        reinstall_available=[
            yumpkg('kernel', '2.6.32', '128-9.el6', 'x86_64'),
            yumpkg('grub', '0.99', '1.el6', 'x86_64')
        ]
    ),
    downloadPkgs=lambda packages: True,
    repos=flexmock(
        repos={},
        add=lambda *args, **kwargs: True,
        enableRepo=lambda *args, **kwargs: True
    )
)
yum.yumRepo = flexmock()
yum.yumRepo.YumRepository = flexmock(
    pkgdir='/pkgdir'
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

    def test_with_baseurl(self):
        #(yum.YumBase
        #    .should_receive('add_enable_repo')
        #    .once
        #    .with_args('repo1', baseurls=['http://url1'])
        #    .and_return(flexmock))
        repo = pakrat.repo.factory(name='repo1', baseurls=['http://url1'])
        assert_equals(repo.id, 'repo1')
        assert_equals(len(repo.baseurls), 1)
        assert_equals(repo.baseurls[0], 'http://url1')

    def test_with_multiple_baseurls(self):
        repo = pakrat.repo.factory(
            name='repo1',
            baseurls=['http://url1', 'http://url2']
        )
        assert_equals(len(repo.baseurls), 2)

    def test_url_types(self):
        assert pakrat.repo.factory(
            name='repo1',
            baseurls=['http://url1', 'https://url2', 'file:///url3']
        )
        assert pakrat.repo.factory(name='repo1', mirrorlist='http://url1')
        assert pakrat.repo.factory(name='repo2', mirrorlist='https://url2')

    @raises(Exception)
    def test_baseurl_exception(self):
        pakrat.repo.factory(name='repo1', baseurls=['http://good', 'bad'])

    @raises(Exception)
    def test_mirrorlist_exception(self):
        pakrat.repo.factory(name='repo1', mirrorlist='bad')

    @raises(Exception)
    def test_mirrorlist_with_file_url(self):
        pakrat.repo.factory(name='repo1', mirrorlist='file:///url1')

class test_set_repo_path:

    def test_set_repo_path(self):
        repo = pakrat.repo.factory(name='repo1', baseurls=['http://url1'])
        pkgdir_before = repo.pkgdir
        pakrat.repo.set_path(repo, '/newdir')
        pkgdir_after = repo.pkgdir
        assert_not_equals(pkgdir_before, pkgdir_after)
        assert_equals(pkgdir_after, '/newdir')

class test_create_metadata:

    def test_create_metadata(self):
        #(mocks['createrepo.SplitMetaDataGenerator']
        #    .should_receive('doPkgMetadata').times(1))
        #(mocks['createrepo.SplitMetaDataGenerator']
        #    .should_receive('doRepoMetadata').times(1))
        #(mocks['createrepo.SplitMetaDataGenerator']
        #    .should_receive('doFinalMove').times(1))
        repo = pakrat.repo.factory(name='repo1', baseurls=['http://url1'])
        pakrat.repo.create_metadata(repo)

class test_sync_repo:

    def setUp(self):
        flexmock(sys.modules['os'], makedirs=lambda *args: True)
        flexmock(sys.modules['os'], symlink=lambda *args, **kwargs: True)

    def test_sync_repo(self):
        repo = pakrat.repo.factory(name='repo1', baseurls=['http://url1'])
        pakrat.repo.sync(repo, '/tmp/pakrat')
