from bottle import get, post, run
import yum
import json

@get('/')
def root():
    repos = [
        #{ 'name': 'centos-base', 'mirrorlist': 'http://mirrorlist.centos.org/?release=6&arch=x86_64&repo=os' },
        #{ 'name': 'centos-updates', 'baseurl': 'http://mirror.centos.org/centos/6/updates/x86_64' }
        { 'name': 'epel', 'baseurl': 'http://dl.fedoraproject.org/pub/epel/6/x86_64' }
    ]

    yb = yum.YumBase()
    yb.repos.disableRepo('*')

    for repo in repos:
        if 'mirrorlist' in repo.keys():
            yb.add_enable_repo(repo['name'], mirrorlist=repo['mirrorlist'])
        elif 'baseurl' in repo.keys():
            yb.add_enable_repo(repo['name'], baseurls=[repo['baseurl']])

    result = []
    packages = yb.doPackageLists(pkgnarrow='available')
    for pkg in packages:
        result.append(pkg.name)
    return json.dumps(result, indent=2)

run(host='0.0.0.0')
