Pakrat
-------

A tool to mirror and version YUM repositories

What does it do?
----------------

* You invoke pakrat and pass it some information about your repositories.
* Pakrat mirrors the YUM repositories, and optionally arranges the data in a
  versioned manner.

It is easiest to demonstrate what Pakrat does by shell example:
```
$ pakrat \
>   --name os \
>   --baseurl http://mirror.centos.org/centos/6/os/x86_64 \
>   --name updates \
>   --baseurl http://mirror.centos.org/centos/6/updates/x86_64 \
>   --name extras \
>   --baseurl http://mirror.centos.org/centos/6/extras/x86_64

  repo              done/total       complete    metadata
  -------------------------------------------------------
  extras              13/13          100%        complete  
  os                 357/6381        5%          -         
  updates            112/1100        10%         -         

  total:             482/7494        6%

```

Features
--------

* Mirror repository packages from remote sources
* Optional repository versioning with user-defined version schema
* Mirror YUM group metadata
* Supports standard YUM configuration files
* Supports YUM configuration directories (repos.d style)
* Command-line interface with real-time progress indicator
* Parallel repository downloads for maximum effeciency
* Syslog integration
* Supports user-specified callbacks

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

The simplest possible example would involve mirroring a YUM repository in a
very basic way, using the CLI:

```
$ pakrat --name centos --baseurl http://mirror.centos.org/centos/6/os/x86_64
$ tree -d centos
centos/
├── Packages
└── repodata
```

A slightly more complex example would be to version the same repository. To
do this, you must pass in a version number. An easy example is to mirror a
repository daily.
```
$ pakrat \
    --repoversion $(date +%Y-%m-%d) \
    --name centos \
    --baseurl http://mirror.centos.org/centos/6/os/x86_64
$ tree -d centos
centos/
├── 2013-07-29
│   ├── Packages -> ../Packages
│   └── repodata
├── latest -> 2013-07-29
└── Packages
```

If you were to configure the above to command to run on a daily schedule,
eventually you would see something like:
```
$ tree -d centos
centos/
├── 2013-07-29
│   ├── Packages -> ../Packages
│   └── repodata
├── 2013-07-30
│   ├── Packages -> ../Packages
│   └── repodata
├── 2013-07-31
│   ├── Packages -> ../Packages
│   └── repodata
├── latest -> 2013-07-31
└── Packages
```

Pakrat is also capable of handling multiple YUM repositories in the same mirror
run. If multiple repositories are specified, each repository will get its own
download thread. This is handy if you are syncing from a mirror that is not
particularly quick. The other repositories do not need to wait on it to finish.
```
$ pakrat \
    --repoversion $(date +%Y-%m-%d) \
    --name centos --baseurl http://mirror.centos.org/centos/6/os/x86_64 \
    --name epel --baseurl http://dl.fedoraproject.org/pub/epel/6/x86_64
$ tree -d centos epel
centos/
├── 2013-07-29
│   ├── Packages -> ../Packages
│   └── repodata
├── latest -> 2013-07-29
└── Packages
epel/
├── 2013-07-29
│   ├── Packages -> ../Packages
│   └── repodata
├── latest -> 2013-07-29
└── Packages
```

Configuration can also be passed in from YUM configuration files. See the CLI
`--help` for details.

Pakrat also exposes its interfaces in plain python for integration with other
projects and software. A good starting point for using Pakrat via the python
API is to take a look at the `pakrat.sync` method. The CLI calls this method
almost exclusively, so it should be fairly straightforward in its usage:
```
pakrat.sync(basedir, objrepos=[], repodirs=[], repofiles=[], repoversion=None, delete=False)
```

Another handy python method is `pakrat.repo.factory`, which creates YUM
repository objects so that no file-based configuration is needed.
```
pakrat.factory(name, baseurls=None, mirrorlist=None)
```

User-defined callbacks
----------------------

Since the YUM team did a decent job at externalizing the progress data,
pakrat will return the favor by exposing the same data, plus some extras
via user callbacks.

A user callback is a simple class that implements some methods for handling
received data. It is not mandatory to implement any of the methods.

A few of the available user callbacks in pakrat come directly from the
`urlgrabber` interface (namely, any user callback beginning with `download_`.
The other methods are called by pakrat, which explains why the interfaces
are varied.

The following user callbacks are supported:

* `repo_init(repo_id, num_pkgs)`: Called when the number of packages a
  repository contains becomes known
* `repo_metadata(repo_id, status)`: Called when `createrepo` begins
  running and when it completes. `status` will be a string containing
  either "working" or "complete".
* `repo_complete(repo_id)`: Called when a repository finishes downloading
  all packages.
* `download_start(repo_id, fpath, url, fname, fsize, text)`: Called when
  a file begins downloading. Note that this will not return only RPM
  packages but also repodata files etc.
* `download_update(repo_id, size)`: Called throughout the course of a
  file download. `size` is the amount of data downloaded so far in bytes.
* `download_end(repo_id, size)`: Called when a file download completes.
  `size` is the total size downloaded.

The following is a basic example of how to use user callbacks in pakrat.
Note that an instance of the class is passed into the `pakrat.sync()` call
as an argument, called `callback`.

```
import pakrat

class mycallback(object):
    def log(self, msg):
        with open('log.txt', 'a') as logfile:
            logfile.write('%s\n' % msg)

    def repo_init(self, repo_id, num_pkgs):
        self.log('Found %d packages in repo %s' % (num_pkgs, repo_id))

    def download_start(self, repo_id, _file, url, basename, size, text):
        self.fname = basename

    def download_end(self, repo_id, size):
        if self.fname.endswith('.rpm'):
            self.log('%s, repo %s, size %d' % (self.fname, repo_id, size))

    def repo_metadata(self, repo_id, status):
        self.log('Metadata for repo %s is now %s' % (repo_id, status))

myrepo = pakrat.repo.factory(
    'extras',
    mirrorlist='http://mirrorlist.centos.org/?repo=extras&release=6&arch=x86_64'
)

mycallback_instance = mycallback()
pakrat.sync(objrepos=[myrepo], callback=mycallback_instance)
```

If you run the above example, and then take a look in the `log.txt` file (which
the user callbacks should have created), you will see something like:

```
Found 13 packages in repo extras
bakefile-0.2.8-3.el6.centos.x86_64.rpm, repo extras, size 256356
centos-release-cr-6-0.el6.centos.x86_64.rpm, repo extras, size 3996
centos-release-xen-6-2.el6.centos.x86_64.rpm, repo extras, size 4086
freenx-0.7.3-9.4.el6.centos.x86_64.rpm, repo extras, size 99256
jfsutils-1.1.13-9.el6.x86_64.rpm, repo extras, size 244104
nx-3.5.0-2.1.el6.centos.x86_64.rpm, repo extras, size 2807864
opennx-0.16-724.el6.centos.1.x86_64.rpm, repo extras, size 1244240
python-empy-3.3-5.el6.centos.noarch.rpm, repo extras, size 104632
wxBase-2.8.12-1.el6.centos.x86_64.rpm, repo extras, size 586068
wxGTK-2.8.12-1.el6.centos.x86_64.rpm, repo extras, size 3081804
wxGTK-devel-2.8.12-1.el6.centos.x86_64.rpm, repo extras, size 1005036
wxGTK-gl-2.8.12-1.el6.centos.x86_64.rpm, repo extras, size 31824
wxGTK-media-2.8.12-1.el6.centos.x86_64.rpm, repo extras, size 38644
Metadata for repo extras is now working
Metadata for repo extras is now complete
```

Building an RPM
---------------

Pakrat can be easily packaged into an RPM.

1. Download a release and name the tarball `pakrat.tar.gz`:
```
curl -o pakrat.tar.gz -L https://github.com/ryanuber/pakrat/archive/master.tar.gz
```

2. Build it into an RPM:
```
rpmbuild -tb pakrat.tar.gz
```

What's missing
--------------

* Optional "all" repository containing all known versions
* Combined repositories?

Thanks
------

Thanks to [Keith Chambers](https://github.com/keithchambers) for help with the ideas
and useful input on CLI design.
