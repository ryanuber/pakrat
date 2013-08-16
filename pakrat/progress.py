import sys
import datetime

class Progress(object):

    repos = {}
    prevlines = 0

    def __init__(self):
        self.start = datetime.datetime.now()

    def update(self, repo, set_total=None, add_downloaded=None):
        if not self.repos.has_key(repo.id):
            self.repos[repo.id] = {'numpkgs':0, 'dlpkgs':0}
        if set_total:
            self.repos[repo.id]['numpkgs'] = set_total
        if add_downloaded:
            self.repos[repo.id]['dlpkgs'] += add_downloaded
        self.formatted()

    @staticmethod
    def pct(current, total):
        return int((current / float(total)) * 100)

    def elapsed(self):
        return str(datetime.datetime.now() - self.start).split('.')[0]

    def format_line(self, reponame, downloaded, total, percent):
        return '  %-15s  %5s/%-10s  %s' % (reponame, downloaded, total,
                                           percent)

    def repostr(self, repo):
        if self.repos[repo]['numpkgs'] > 0:
            percent = '%s%%' % self.pct(self.repos[repo]['dlpkgs'],
                                        self.repos[repo]['numpkgs'])
        else:
            percent = '-'
        return self.format_line(repo, self.repos[repo]['dlpkgs'],
                                self.repos[repo]['numpkgs'], percent)

    def formatted(self):
        sys.stdout.write('\033[F\033[K' * self.prevlines)
        self.prevlines = 3  # start with 3 to compensate for header
        header = self.format_line('repo', 'done', 'totalpkgs',
                                  'complete')
        sys.stdout.write('\n%s\n' % header)
        sys.stdout.write('%s\n' % ('-' * len(header)))
        for repo in self.repos.keys():
            sys.stdout.write('%s\n' % self.repostr(repo))
            self.prevlines += 1
        sys.stdout.flush()

    def complete_all(self):
        for repo in self.repos.keys():
            self.repos[repo]['dlpkgs'] = self.repos[repo]['numpkgs']
        self.formatted()

class YumProgress(object):

    def __init__(self, repo, progress):
        self.repo = repo
        self.progress = progress

    def start(self, _file, url, basename, size, text):
        self._file = _file

    def update(self, size):
        pass

    def end(self, size):
        if self._file.endswith('.rpm'):
            self.progress.update(self.repo, add_downloaded=1)
