import yum

repos = [
    {
        'name':       'centos-base',
        'mirrorlist': 'http://mirrorlist.centos.org/?release=6.4&arch=x86_64&repo=os',
        'arch':       ['x86-64']
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

yb = yum.YumBase()
yb.repos.disableRepo('*')

for repo in repos:
    if 'mirrorlist' in repo.keys():
        yb.add_enable_repo(repo['name'], mirrorlist=repo['mirrorlist'])
    elif 'baseurl' in repo.keys():
        yb.add_enable_repo(repo['name'], baseurls=[repo['baseurl']])
    if 'arch' in repo.keys() and type(repo['arch']) is list:
        yb.doSackSetup(thisrepo=repo['name'], archlist=repo['arch'])

result = []
packages = yb.doPackageLists(pkgnarrow='available', showdups=False)
for pkg in packages:
    print '%s-%s.%s' % (pkg.name, pkg.version, pkg.arch)
