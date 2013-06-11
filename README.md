PackRat
-------

A completely stateless library to sync YUM repositories from multiple sources

How to use it
-------------

### Specify some *.repo file paths to load repositories from:

```python
pakrat.sync('/root/mirrors', repofiles=['/root/yumrepos/CentOS-Base.repo'])
```

### Load from a repos.d directory

You can pass in multiple directories to load:

```python
from pakrat import sync
sync('/root/mirrors', repodirs=['/root/yumrepos'])
```

### Direct Python library calls

```python
from pakrat import repo, sync
sync('/root/mirrors', repos=[
    repo('base', baseurls=['http://mirror.centos.org/centos/6/os/x86_64']),
    repo('updates', baseurls=['http://mirror.centos.org/centos/6/updates/x86_64']),
    repo('epel', baseurls=['http://dl.fedoraproject.org/pub/epel/6/x86_64'])
])
```

### Mix and Match

Keep in mind that you can mix all 3 of the above input types. You can have
repository directories, files, and in-line definitions all working together
additively.

```python
from pakrat import repo, sync
inline_repos = [
    repo('epel', baseurls=['http://dl.fedoraproject.org/pub/epel/6/x86_64'])
]
repo_dirs = [ '/etc/yum.repos.d' ]
repo_files = [ '/root/my-yum-repo.conf' ]
sync('/root/mirrors', repos=inline_repos, repodirs=repo_dirs, repofiles = repo_files)
```

CLI interface
-------------

```
Usage: pakrat [options]

Options:
  -h, --help            show this help message and exit
  --dest=DEST           
  -d REPODIR, --repodir=REPODIR
  -f REPOFILE, --repofile=REPOFILE
```

```
$ pakrat --dest /root/mirrors/ --repodir /etc/yum.repos.d/
debug: Not adding repo contrib because it is disabled
debug: Not adding repo centosplus because it is disabled
info: Added repo base from file /root/yumrepos/CentOS-Base.repo
info: Added repo updates from file /root/yumrepos/CentOS-Base.repo
debug: Not adding repo extras because it is disabled
info: Downloading packages from repository base
info: Finished downloading packages from repository base
debug: Unlinking /root/mirrors/base/latest because it is outdated
debug: Linking /root/mirrors/base/latest to 5-19-2013
info: Downloading packages from repository updates
info: Finished downloading packages from repository updates
debug: Unlinking /root/mirrors/updates/latest because it is outdated
debug: Linking /root/mirrors/updates/latest to 5-19-2013
```
