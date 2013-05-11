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

now = datetime.now()
repo_version = '%s-%s-%s' % (now.month, now.day, now.year)

for repo in conf['repos']:
    yb = yum.YumBase()
    yb.repos.disableRepo('*')
    yb.setCacheDir(force=True, reuse=False, tmpdir=yum.misc.getCacheDir())

    repo_dir = '%s/%s/packages' % (conf['mirror_dir'], repo['name'])
    versioned_dir = '%s/%s/%s' % (conf['mirror_dir'], repo['name'], repo_version)

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

    for file in os.listdir(repo_dir):
        symlink = '%s/%s' % (versioned_dir, file)
        link_to = '../packages/%s' % file
        if not os.path.exists(symlink):
            os.symlink(link_to, symlink)
