import yum

class yumbase(yum.YumBase):

    def __init__(self):
        yum.YumBase.__init__(self)
        self.preconf = yum._YumPreBaseConf()
        self.preconf.debuglevel = 0
        self.prerepoconf = yum._YumPreRepoConf()
        self.setCacheDir(force=True, reuse=False, tmpdir=yum.misc.getCacheDir())
        self.repos.repos = {}
