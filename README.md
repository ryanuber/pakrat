Pakrat
-------

A stateless python library and CLI tool to sync and version YUM repositories
from multiple sources

What does it do?
----------------

* You invoke pakrat and pass in a few YUM repos (see below for how to do
  this)
* Pakrat fetches all packages found in the repositories you specified and saves
  them into a shared `packages` directory.
* Pakrat uses the `createrepo` library to compile metadata about the packages
  that were downloaded and saves it into a versioned directory (see explanation
  below)
* You expose the top-level directory with any HTTP server, and you now have
  access to versioned YUM repositories!

Features
-------

* Data deduplication by using a common packages directory. Each run, the only
  new data created is the repodata (usually a few Mb)
* Threaded downloading and repo creation
* CLI provides easy interface for use by CRON or similar scheduler
* Supports multiple baseurls
* Supports mirrorlists

Installation
------------

Pakrat is available in PyPI as `pakrat`. That means you can install it with
easy_install:

```
# easy_install pakrat
```

*NOTE*
Installation from PyPI should work on any Linux. However, since Pakrat depends
on YUM and Createrepo, which are not available in PyPI, these dependencies will
not be detected as missing. The easiest install path is to install on some kind
of RHEL like so:

```
# yum -y install createrepo
# easy_install pakrat
```

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

### Inline repositories using `repo()`
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
sync('/root/mirrors', repos=inline_repos, repodirs=repo_dirs, repofiles=repo_files)
```

### Repository versioning
By default, repositories will be versioned as YYYY-MM-DD. This means that if a
repository is synced more than once per day, it will overwrite any existing
packages from previous runs that day. You can create any versioning scheme you
like though, by passing in the version rather than letting Pakrat do it for you.
Below is an example using a unix timestamp instead of the default:

Library:
```python
pakrat.sync('...', baseurls=[...], repoversion=int(time.time()))
```

CLI:
```
pakrat --dest ... --repofile ... --repoversion `date +%s`
```

CLI interface
-------------

```
Usage: pakrat [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  --dest=DEST           Root destination for all YUM repositories
  -d REPODIR, --repodir=REPODIR
                        A "repos.d" directory of YUM configurations.
                        (repeatable)
  -f REPOFILE, --repofile=REPOFILE
                        A YUM configuration file. (repeatable)
  -r REPOVERSION, --repoversion=REPOVERSION
                        The version of the repository to create. By default,
                        this will be the current date in format: YYYY-MM-DD
```

Building an RPM
---------------

Pakrat can be easily packaged into an RPM.

1. Download a release:
```
curl -o pakrat.tar.gz -L https://github.com/ryanuber/pakrat/archive/master.tar.gz
```

2. Build it into an RPM:
```
rpmbuild -tb pakrat.tar.gz
```

What's missing
--------------

* Better logging (currently console-only)
