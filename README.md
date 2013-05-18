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
