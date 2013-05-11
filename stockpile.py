import os
import yum
from datetime import datetime

conf = {
    'mirror_dir': '/root/mirrors',
    'repos': [
        {
            'name':       'centos-base',
            'mirrorlist': 'http://mirrorlist.centos.org/?release=6.4&arch=x86_64&repo=os',
            'arch':       ['x86_64']
        },
        {
            'name':    'centos-updates',
            'baseurl': 'http://mirror.centos.org/centos/6/updates/x86_64',
            'arch':    ['x86_64']
        },
        {
            'name':    'epel',
            'baseurl': 'http://dl.fedoraproject.org/pub/epel/6/x86_64',
            'arch':    ['x86_64']
        },
    ]
}

for repo in conf['repos']:
    yb = yum.YumBase()
    yb.repos.disableRepo('*')
    yb.setCacheDir(force=True, reuse=False, tmpdir=yum.misc.getCacheDir())

    now = datetime.now()
    repo_version = '%s-%s-%s' % (now.month, now.day, now.year)

    base_dir = '%s/%s' % (conf['mirror_dir'], repo['name'])
    repo_dir = '%s/packages' % base_dir
    versioned_dir = '%s/%s' % (repo_dir, repo_version)
    latest_symlink = '%s/latest' % base_dir

    if 'mirrorlist' in repo.keys():
        yr = yb.add_enable_repo(repo['name'], mirrorlist=repo['mirrorlist'])
    elif 'baseurl' in repo.keys():
        yr = yb.add_enable_repo(repo['name'], baseurls=[repo['baseurl']])
    if 'arch' in repo.keys() and type(repo['arch']) is list:
        yb.doSackSetup(thisrepo=repo['name'], archlist=repo['arch'])

    yr._dirSetAttr('pkgdir', repo_dir)

    packages = yb.doPackageLists(pkgnarrow='available', showdups=False)
    yb.downloadPkgs(packages)

    if not os.path.exists(versioned_dir):
        os.makedirs(versioned_dir)

    for pkg in packages:
        pkg_name_full = '%s-%s-%s.%s' % (pkg.name, pkg.version, pkg.release, pkg.arch)
        symlink = '%s/%s' % (versioned_dir, pkg_name_full)
        link_to = '../packages/%s' % pkg_name_full
        if not os.path.exists(symlink):
            os.symlink(link_to, symlink)

    if os.path.exists(latest_symlink) and os.readlink(latest_symlink) is not repo_version:
        os.unlink(latest_symlink)

    os.symlink(repo_version, latest_symlink)
