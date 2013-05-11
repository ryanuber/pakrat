from bottle import get, post, run
import yum
import json

@get('/')
def root():
    yb = yum.YumBase()
    #add_enable_repo(self, repoid, baseurls=[], mirrorlist=None)
    result = []
    packages = yb.doPackageLists(pkgnarrow='available')
    for pkg in packages:
        result.append(pkg.name)
    return json.dumps(result, indent=2)

run(host='0.0.0.0')
