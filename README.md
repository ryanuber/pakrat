Stockpile
---------

A completely stateless library to sync YUM repositories from multiple sources

---

Specify some *.repo file paths to load repositories from:

```
Stockpile.sync('/root/mirrors', repofiles=['/root/yumrepos/CentOS-Base.repo'])
```

Load in some repositories from a repos.d-style directory. You can pass in
multiple directories to load:

```
Stockpile.sync('/root/mirrors', repodirs=['/root/yumrepos'])
```

No configuration on disk? No problem! Pass in the repo data directly using
Stockpile's built-in repo generating method:

```
Stockpile.sync('/root/mirrors', [
    Stockpile.repo('centos-base', ['x86_64'], ['http://mirror.centos.org/centos/6/os/x86_64']),
    Stockpile.repo('centos-updates', ['x86_64'], ['http://mirror.centos.org/centos/6/updates/x86_64']),
    Stockpile.repo('epel', ['x86_64'], ['http://dl.fedoraproject.org/pub/epel/6/x86_64'])
])
```

Keep in mind that you can mix all 3 of the above input types. You can have
repository directories, files, and in-line definitions all working together
additively.

CLI interface:

```
$ python stockpile.py  --dest /root/mirrors/ --repodir /root/yumrepos/
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
