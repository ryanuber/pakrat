import sys
import datetime

class Progress(object):

    repos = {}
    total = {'dlpkgs':0, 'numpkgs':0}
    prevlines = 0

    def __init__(self):
        self.start = datetime.datetime.now()

    def update(self, repo, total=None, downloaded=None):
        if not self.repos.has_key(repo.id):
            self.repos[repo.id] = {'total':0, 'dlpkgs':0}
        if total:
            self.repos[repo.id]['numpkgs'] = total
        if downloaded:
            self.repos[repo.id]['dlpkgs'] = downloaded
        self.update_totals(total=total, downloaded=downloaded)
        self.formatted()

    def update_totals(self, total=None, downloaded=None):
        if downloaded:
            self.total['dlpkgs'] += downloaded
        if total:
            self.total['numpkgs'] += total

    @staticmethod
    def pct(current, total):
        return int((current / float(total)) * 100)

    def elapsed(self):
        return str(datetime.datetime.now() - self.start).split('.')[0]

    def format_line(self, reponame, downloaded, total, percent):
        return '  %-15s  %5s/%-10s  %s' % (reponame, downloaded, total,
                                           percent)

    def repostr(self, repo):
        percent = '%s%%' % self.pct(self.repos[repo]['dlpkgs'],
                                    self.repos[repo]['numpkgs'])
        return self.format_line(repo, self.repos[repo]['dlpkgs'],
                                self.repos[repo]['numpkgs'], percent)

    def formatted(self):
        sys.stdout.write('\033[F' * self.prevlines)
        self.prevlines = 3  # start with 3 to compensate for header
        header = self.format_line('repo', 'done', 'totalpkgs',
                                  'complete')
        sys.stdout.write('\n%s\n' % header)
        sys.stdout.write('%s\n' % ('-' * len(header)))
        for repo in self.repos.keys():
            sys.stdout.write('\033[K')
            sys.stdout.write('%s\n' % self.repostr(repo))
            self.prevlines += 1
        sys.stdout.flush()

class repo(object):
    def __init__(self, name):
        self.id = name


if __name__ == '__main__':
    import time
    x = repo('os')
    z = repo('updates')
    y = Progress()
    y.update(x, 6384, 5)
    y.update(z, 1100, 2)
    time.sleep(1)
    y.update(x, downloaded=248)
    time.sleep(0.3)
    y.update(z, 1100, 40)
    time.sleep(2)
    y.update(x, downloaded=405)
    y.update(z, downloaded=603)
    time.sleep(1)
    y.update(x, downloaded=900)
    time.sleep(1)
    y.update(z, downloaded=1025)
    time.sleep(3)
    y.update(x, downloaded=2045)
    time.sleep(1)
    y.update(z, downloaded=1100)
    print
    print
    print
