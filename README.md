Pakrat
-------

A command-line tool to mirror YUM repositories with versioning

What does it do?
----------------

* You invoke pakrat and pass it some repository baseurl's or the path
  to some YUM configurations
* Pakrat mirrors the YUM repositories, and optionally arranges the
  data in a versioned manner.

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

Pakrat is mainly a command-line driven tool. The simplest possible example
would involve mirroring a YUM repository in a very basic way:

```
$ pakrat --name centos --url http://mirror.centos.org/centos/6/os/x86_64
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
    --url http://mirror.centos.org/centos/6/os/x86_64
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
    --name centos \
    --url http://mirror.centos.org/centos/6/os/x86_64 \
    --name epel \
    --url http://dl.fedoraproject.org/pub/epel/6/x86_64
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

Thanks
------

Thanks to [Keith Chambers](https://github.com/keithchambers) for help with the ideas
and useful input on CLI design.
