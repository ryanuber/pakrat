import os
import yum
from pakrat import util, log

def from_file(path):
    """ Read repository configuration from a YUM config file.

    Using the YUM client library, read in a configuration file and return
    a list of repository objects.
    """
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
    """ Read repository configuration from a directory containing YUM configs.

    This method will look through a directory for YUM repository configuration
    files (*.repo) and read them in using the from_file method.
    """
    repos = []
    if os.path.isdir(path):
        for _file in sorted(os.listdir(path)):
            _file = os.path.join(path, _file)
            if not _file.endswith('.repo'):
                continue
            repos += from_file(_file)
    return repos
