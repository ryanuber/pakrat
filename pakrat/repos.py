import os
import yum
from glob import glob
from pakrat import util, log

def from_file(path):
    if not os.path.exists(path):
        raise Exception('No such file or directory: %s' % path)
    yb = util.get_yum()
    yb.getReposFromConfigFile(path)
    for repo in yb.repos.findRepos('*'):
        yb.doSackSetup(thisrepo=repo.getAttribute('name'))
    repos = []
    for repo in yb.repos.findRepos('*'):
        if repo.isEnabled():
            log.info('Added repo %s from file %s' % (repo.id, path))
            repos.append(repo)
        else:
            log.debug('Not adding repo %s because it is disabled' % repo.id)
    return repos

def from_dir(path):
    repos = []
    if os.path.isdir(path):
        for file in sorted(glob('%s/*.repo' % path)):
            for repo in from_file(file):
                repos.append(repo)
    return repos
