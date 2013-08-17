import sys
import datetime

class Progress(object):

    repos = {}
    totals = {'numpkgs':0, 'dlpkgs':0}
    prevlines = 0

    def __init__(self):
        self.start = datetime.datetime.now()

    def update(self, repo_id, set_total=None, add_downloaded=None,
               set_dlcomplete=None, set_repomd=None):
        if not self.repos.has_key(repo_id):
            self.repos[repo_id] = {'numpkgs':0, 'dlpkgs':0, 'repomd':'-'}
        if set_total:
            self.repos[repo_id]['numpkgs'] = set_total
            self.totals['numpkgs'] += set_total
        if add_downloaded:
            self.repos[repo_id]['dlpkgs'] += add_downloaded
            self.totals['dlpkgs'] += add_downloaded
        if set_dlcomplete:
            self.totals['dlpkgs'] += (self.repos[repo_id]['numpkgs'] -
                                      self.repos[repo_id]['dlpkgs'])
            self.repos[repo_id]['dlpkgs'] = self.repos[repo_id]['numpkgs']
        if set_repomd:
            self.repos[repo_id]['repomd'] = set_repomd
        self.formatted()

    @staticmethod
    def pct(current, total):
        return int((current / float(total)) * 100)

    def elapsed(self):
        return str(datetime.datetime.now() - self.start).split('.')[0]

    def format_line(self, reponame, package_counts, percent, repomd):
        return '  %-15s  %-15s  %-10s  %s' % (reponame, package_counts, percent,
                                              repomd)

    def represent_repo_pkgs(self, repo_id):
        numpkgs = self.repos[repo_id]['numpkgs']
        dlpkgs  = self.repos[repo_id]['dlpkgs']
        return self.represent_pkgs(dlpkgs, numpkgs)

    def represent_total_pkgs(self):
        numpkgs = self.totals['numpkgs']
        dlpkgs  = self.totals['dlpkgs']
        return self.represent_pkgs(dlpkgs, numpkgs)

    def represent_pkgs(self, dlpkgs, numpkgs):
        if numpkgs == 0:
            return '%6s%10s' % ('-', ' ')
        else:
            return '%5s/%-10s' % (dlpkgs, numpkgs)

    def represent_repo_percent(self, repo_id):
        numpkgs = self.repos[repo_id]['numpkgs']
        dlpkgs  = self.repos[repo_id]['dlpkgs']
        return self.represent_percent(dlpkgs, numpkgs)

    def represent_total_percent(self):
        numpkgs = self.totals['numpkgs']
        dlpkgs  = self.totals['dlpkgs']
        return self.represent_percent(dlpkgs, numpkgs)

    def represent_percent(self, dlpkgs, numpkgs):
        if numpkgs == 0:
            return '-'
        else:
            return '%s%%' % self.pct(dlpkgs, numpkgs)

    def represent_repomd(self, repo_id):
        return self.repos[repo_id]['repomd']

    def represent_repo(self, repo_id):
        return self.format_line(repo_id, self.represent_repo_pkgs(repo_id),
                                self.represent_repo_percent(repo_id),
                                self.represent_repomd(repo_id))

    def formatted(self):
        if not sys.stdout.isatty():
            return
        sys.stdout.write('\033[F\033[K' * self.prevlines)
        self.prevlines = 3  # start with 3 to compensate for header
        header = self.format_line('repo', '%5s/%-10s' % ('done', 'total'),
                                  'complete', 'metadata')
        sys.stdout.write('\n%s\n' % header)
        sys.stdout.write('  %s\n' % ('-' * (len(header)-2)))
        for repo_id in self.repos.keys():
            sys.stdout.write('%s\n' % self.represent_repo(repo_id))
            self.prevlines += 1
        sys.stdout.write('\n')
        sys.stdout.write(self.format_line('total:', self.represent_total_pkgs(),
                                          self.represent_total_percent(), ''))
        sys.stdout.write('\n')
        self.prevlines += 2
        sys.stdout.flush()

class YumProgress(object):

    def __init__(self, repo_id, queue, usercallback):
        self.repo_id = repo_id
        self.queue = queue
        self.usercallback = usercallback

    def callback(self, method, *args):
        if self.usercallback and hasattr(self.usercallback, method):
            method = getattr(self.usercallback, method)
            try: method(self.repo_id, *args)
            except: pass

    def start(self, _file, url, basename, size, text):
        self._file = _file
        self.callback('download_start', _file, url, basename, size, text)

    def update(self, size):
        self.callback('download_update', size)

    def end(self, size):
        if self._file.endswith('.rpm'):
            self.queue.put({'repo_id':self.repo_id, 'action':'download_end',
                            'value':1})
        self.callback('download_end', size)

class ProgressCallback(object):

    def __init__(self, queue, usercallback):
        self.queue = queue
        self.usercallback = usercallback

    def callback(self, repo_id, event, value):
        if self.usercallback and hasattr(self.usercallback, event):
            method = getattr(self.usercallback, event)
            try: method(repo_id, value)
            except: pass

    def send(self, repo_id, action, value=None):
        self.queue.put({'repo_id':repo_id, 'action': action, 
                        'value':value})
        self.callback(repo_id, action, value)

    def repo_metadata(self, repo_id, value):
        self.send(repo_id, 'repo_metadata', value)

    def repo_init(self, repo_id, numpkgs):
        self.send(repo_id, 'repo_init', numpkgs)

    def repo_complete(self, repo_id):
        self.send(repo_id, 'repo_complete')
