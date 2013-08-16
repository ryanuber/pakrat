import sys
import datetime

class Progress(object):

    repos = {}
    prevlines = 0

    def __init__(self):
        self.start = datetime.datetime.now()

    def update(self, repo_id, set_total=None, add_downloaded=None):
        if not self.repos.has_key(repo_id):
            self.repos[repo_id] = {'numpkgs':0, 'dlpkgs':0}
        if set_total:
            self.repos[repo_id]['numpkgs'] = set_total
        if add_downloaded:
            self.repos[repo_id]['dlpkgs'] += add_downloaded
        self.formatted()

    @staticmethod
    def pct(current, total):
        return int((current / float(total)) * 100)

    def elapsed(self):
        return str(datetime.datetime.now() - self.start).split('.')[0]

    def format_line(self, reponame, downloaded, total, percent):
        return '  %-15s  %5s/%-10s  %s' % (reponame, downloaded, total,
                                           percent)

    def repostr(self, repo_id):
        if self.repos[repo_id]['numpkgs'] > 0:
            percent = '%s%%' % self.pct(self.repos[repo_id]['dlpkgs'],
                                        self.repos[repo_id]['numpkgs'])
        else:
            percent = '-'
        return self.format_line(repo_id, self.repos[repo_id]['dlpkgs'],
                                self.repos[repo_id]['numpkgs'], percent)

    def formatted(self):
        sys.stdout.write('\033[F\033[K' * self.prevlines)
        self.prevlines = 3  # start with 3 to compensate for header
        header = self.format_line('repo', 'done', 'totalpkgs',
                                  'complete')
        sys.stdout.write('\n%s\n' % header)
        sys.stdout.write('%s\n' % ('-' * len(header)))
        for repo_id in self.repos.keys():
            sys.stdout.write('%s\n' % self.repostr(repo_id))
            self.prevlines += 1
        sys.stdout.flush()

    def complete_all(self):
        for repo_id in self.repos.keys():
            self.repos[repo_id]['dlpkgs'] = self.repos[repo_id]['numpkgs']
        self.formatted()

class YumProgress(object):

    def __init__(self, repo_id, queue):
        self.repo_id = repo_id
        self.queue = queue

    def start(self, _file, url, basename, size, text):
        self._file = _file

    def update(self, size):
        pass

    def end(self, size):
        if self._file.endswith('.rpm'):
            self.queue.put({'repo_id':self.repo_id, 'action':'downloaded',
                            'value':1})

class ProgressInit(object):

    def __init__(self, repo_id, queue):
        self.repo_id = repo_id
        self.queue = queue

    def register(self, numpkgs):
        self.queue.put({'repo_id':self.repo_id, 'action':'init',
                        'value':numpkgs})
