import sys
from flexmock import flexmock
from nose.tools import with_setup, assert_true, assert_equals

def setup():
    global sys
    global yum
    global pakrat

    yum = flexmock()
    yum._YumPreBaseConf = flexmock()
    yum._YumPreRepoConf = flexmock()
    yum.misc = flexmock(
        getCacheDir=lambda: '/tmp/pakrat'
    )
    yum.YumBase = flexmock(
        add_enable_repo=lambda *args, **kwargs: flexmock(
            id=args[0],
            baseurls=kwargs['baseurls'] if kwargs.has_key('baseurls') else None
        ),
        setCacheDir=lambda **kwargs: True
    )
    yum.YumBase.repos = flexmock()
    yum.repos = flexmock(
        add=lambda: True
    )

    createrepo = flexmock(
        SplitMetaDataGenerator=lambda: True,
        doPkgMetadata=lambda: True,
        doRepoMetadata=lambda: True,
        doFinalMove=lambda: True
    )
    createrepo.MetaDataConfig = flexmock()
    createrepo.SplitMetaDataGenerator = flexmock()
    createrepo.doPkgMetaData = flexmock()

    sys.modules['yum'] = yum
    sys.modules['createrepo'] = createrepo

    import yum
    import pakrat

@with_setup(setup)
def test_repo_factory():
    #(yum.YumBase.should_receive('add_enable_repo')
    #    .with_args('repoman', baseurls=['http://repoman.com'])
    #    .times(1))
    repo = pakrat.repo.factory(name='repoman', baseurls=['http://repoman.com'])
    assert_equals(repo.id, 'repoman')
    assert_equals(len(repo.baseurls), 1)
    assert_equals(repo.baseurls[0], 'http://repoman.com')
