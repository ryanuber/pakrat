import yum

""" YumBase object specifically for pakrat.

This class is a simple extension of the yum.YumBase class. It is required
because pakrat uses YUM in an atypical way. When we load a YUM object, we want
only the scaffolding, and none of the system repositories or other inherited
configuration. This sounds easy but is not really built-in to YUM. This method
also uses the YUM client library to create its own cachedir on instantiation.
"""
class YumBase(yum.YumBase):

    def __init__(self):
        """ Create a new YumBase object for use in pakrat. """
        yum.YumBase.__init__(self)
        self.preconf = yum._YumPreBaseConf()
        self.preconf.debuglevel = 0
        self.prerepoconf = yum._YumPreRepoConf()
        self.setCacheDir(force=True, reuse=False,
                         tmpdir=yum.misc.getCacheDir())
        self.repos.repos = {}
