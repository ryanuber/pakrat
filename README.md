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

* Better logging (currently console-only)
* Optional "all" repository containing all known versions
* Combined repositories?

Thanks
------

Thanks to [Keith Chambers](https://github.com/keithchambers) for help with the ideas
and useful input on CLI design.
