# pakrat - A tool for mirroring and versioning YUM repositories.
# Copyright 2013 Ryan Uber <ru@ryanuber.com>. All rights reserved.
#
# MIT LICENSE
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
import datetime

class Progress(object):
    """ Handle progress indication using callbacks.

    This class will create an object that stores information about a
    running pakrat process. It stores information about each repository
    being synced, including total packages, completed packages, and
    the status of the repository metadata. This makes it possible to
    display aggregated status of multiple repositories during a sync.
    """
    repos = {}
    totals = {'numpkgs':0, 'dlpkgs':0, 'errors':0}
    errors = []
    prevlines = 0

    def __init__(self):
        """ Simply records the time the sync started. """
        self.start = datetime.datetime.now()

    def update(self, repo_id, set_total=None, pkgs_downloaded=None,
               repo_complete=None, repo_metadata=None, repo_error=None):
        """ Handles updating the object itself.

        This method will be called any time the number of packages in
        a repository becomes known, when any package finishes downloading,
        when repository metadata begins indexing and when it completes.
        """
        if not self.repos.has_key(repo_id):
            self.repos[repo_id] = {'numpkgs':0, 'dlpkgs':0, 'repomd':'-'}
        if set_total:
            self.repos[repo_id]['numpkgs'] = set_total
            self.totals['numpkgs'] += set_total
        if pkgs_downloaded:
            self.repos[repo_id]['dlpkgs'] += pkgs_downloaded
            self.totals['dlpkgs'] += pkgs_downloaded
        if repo_complete:
            self.totals['dlpkgs'] += (self.repos[repo_id]['numpkgs'] -
                                      self.repos[repo_id]['dlpkgs'])
            self.repos[repo_id]['dlpkgs'] = self.repos[repo_id]['numpkgs']
        if repo_metadata:
            self.repos[repo_id]['repomd'] = repo_metadata
        if repo_error:
            self.totals['errors'] += 1
            self.errors.append((repo_id, repo_error))
        self.formatted()

    @staticmethod
    def pct(current, total):
        """ Calculate a percentage. """
        return int((current / float(total)) * 100)

    def elapsed(self):
        """ Calculate and return elapsed time.

        This function does dumb rounding by just plucking off anything past a
        dot "." in a time delta between two datetime.datetime()'s.
        """
        return str(datetime.datetime.now() - self.start).split('.')[0]

    def format_line(self, reponame, package_counts, percent, repomd):
        """ Return a string formatted for output.

        Since there is a common column layout in the progress indicator, we can
        we can implement the printf-style formatter in a function.
        """
        return '%-15s  %-15s  %-10s  %s' % (reponame, package_counts, percent,
                                            repomd)

    def represent_repo_pkgs(self, repo_id):
        """ Format the ratio of packages in a repository. """
        numpkgs = self.repos[repo_id]['numpkgs']
        dlpkgs  = self.repos[repo_id]['dlpkgs']
        return self.represent_pkgs(dlpkgs, numpkgs)

    def represent_total_pkgs(self):
        """ Format the total number of packages in all repositories. """
        numpkgs = self.totals['numpkgs']
        dlpkgs  = self.totals['dlpkgs']
        return self.represent_pkgs(dlpkgs, numpkgs)

    def represent_pkgs(self, dlpkgs, numpkgs):
        """ Represent a package ratio.

        This will display nothing if the number of packages is 0 or unknown, or
        typical done/total if total is > 0.
        """
        if numpkgs == 0:
            return '%6s%10s' % ('-', ' ')
        else:
            return '%5s/%-10s' % (dlpkgs, numpkgs)

    def represent_repo_percent(self, repo_id):
        """ Display the percentage of packages downloaded in a repository. """
        numpkgs = self.repos[repo_id]['numpkgs']
        dlpkgs  = self.repos[repo_id]['dlpkgs']
        return self.represent_percent(dlpkgs, numpkgs)

    def represent_total_percent(self):
        """ Display the overall percentage of downloaded packages. """
        numpkgs = self.totals['numpkgs']
        dlpkgs  = self.totals['dlpkgs']
        return self.represent_percent(dlpkgs, numpkgs)

    def represent_percent(self, dlpkgs, numpkgs):
        """ Display a percentage of completion.

        If the number of packages is unknown, nothing is displayed. Otherwise,
        a number followed by the percent sign is displayed.
        """
        if numpkgs == 0:
            return '-'
        else:
            return '%s%%' % self.pct(dlpkgs, numpkgs)

    def represent_repomd(self, repo_id):
        """ Display the current status of repository metadata. """
        return self.repos[repo_id]['repomd']

    def represent_repo(self, repo_id):
        """ Represent an entire repository in one line.

        This makes calls to the other methods of this class to create a
        formatted string, which makes nice columns.
        """
        if self.repos[repo_id].has_key('error'):
            packages = '     error'
            percent  = ''
            metadata = ''
        else:
            packages = self.represent_repo_pkgs(repo_id)
            percent  = self.represent_repo_percent(repo_id)
            metadata = self.represent_repomd(repo_id)
        return self.format_line(repo_id, packages, percent, metadata)

    def emit(self, line=''):
        self.prevlines += len(line.split('\n'))
        sys.stdout.write('%s\n' % line)

    def formatted(self):
        """ Print all known progress data in a nicely formatted table.

        This method keeps track of what it has printed before, so that it can
        backtrack over the console screen, clearing out the previous flush and
        printing out a new one. This method is called any time any value is
        updated, which is what gives us that real-time feeling.

        Unforutnately, the YUM library calls print directly rather than just
        throwing exceptions and handling them in the presentation layer, so
        this means that pakrat's output will be slightly flawed if YUM prints
        something directly to the screen from a worker process.
        """
        if not sys.stdout.isatty():
            return
        sys.stdout.write('\033[F\033[K' * self.prevlines)  # clears lines
        self.prevlines = 0  # reset line counter
        header = self.format_line('repo', '%5s/%-10s' % ('done', 'total'),
                                  'complete', 'metadata')
        self.emit('\n%s' % header)
        self.emit(('-' * len(header)))

        # Remove repos with errors from totals
        if self.totals['errors'] > 0:
            for repo_id, error in self.errors:
                if repo_id in self.repos.keys():
                    self.totals['dlpkgs'] -= self.repos[repo_id]['dlpkgs']
                    self.totals['numpkgs'] -= self.repos[repo_id]['numpkgs']
                    #del self.repos[repo_id]
                    self.repos[repo_id]['error'] = True

        for repo_id in self.repos.keys():
            self.emit(self.represent_repo(repo_id))
        self.emit()
        self.emit(self.format_line('total:', self.represent_total_pkgs(),
                                   self.represent_total_percent(), ''))
        self.emit()

        # Append errors to output if any found.
        if self.totals['errors'] > 0:
            self.emit('errors(%d):' % self.totals['errors'])
            for repo_id, error in self.errors:
                self.emit(error)
            self.emit()

        sys.stdout.flush()

class YumProgress(object):
    """ Creates an object for passing to YUM for status updates.

    YUM allows you to pass in your own callback object, which urlgrabber will
    use directly by calling some methods on it. Here we have an object that can
    be prepared with a repository ID, so that we can know which repository it
    is that is making the calls back.
    """
    def __init__(self, repo_id, queue, usercallback):
        """ Create the instance and set prepared config """
        self.repo_id = repo_id
        self.queue = queue
        self.usercallback = usercallback

    def callback(self, method, *args):
        """ Abstracted callback function to reduce boilerplate.

        This is actually quite useful, because it checks that the method exists
        on the callback object before trying to invoke it, making all methods
        optional.
        """
        if self.usercallback and hasattr(self.usercallback, method):
            method = getattr(self.usercallback, method)
            try: method(self.repo_id, *args)
            except: pass

    def start(self, _file, url, basename, size, text):
        """ Called by urlgrabber when a file download starts.

        All we use this for is storing the name of the file being downloaded so
        we can check that it is an RPM later on.
        """
        self.package = basename
        self.callback('download_start', _file, url, basename, size, text)

    def update(self, size):
        """ Called during the course of a download.

        Pakrat does not use this for anyting, but we'll be a good neighbor and
        pass the data on to the user callback.
        """
        self.callback('download_update', size)

    def end(self, size):
        """ Called by urlgrabber when it completes a download.

        Here we have to check the file name saved earlier to make sure it is an
        RPM we are getting the event for.
        """
        if self.package.endswith('.rpm'):
            self.queue.put({'repo_id':self.repo_id, 'action':'download_end',
                            'value':1})
        self.callback('download_end', size)

class ProgressCallback(object):
    """ Register our own callback for progress indication.

    This class allows pakrat to stuff a user callback into an object before
    forking a thread, so that we don't have to keep making calls to multiple
    callbacks everywhere.
    """
    def __init__(self, queue, usercallback):
        """ Create a new progress object.

        This method allows the main process to pass its multiprocessing.Queue()
        object in so we can talk back to it.
        """
        self.queue = queue
        self.usercallback = usercallback

    def callback(self, repo_id, event, value):
        """ Abstracts calling the user callback. """
        if self.usercallback and hasattr(self.usercallback, event):
            method = getattr(self.usercallback, event)
            try: method(repo_id, value)
            except: pass

    def send(self, repo_id, action, value=None):
        """ Send an event to the main queue for processing.

        This gives us the ability to pass data back to the parent process,
        which is mandatory to do aggregated progress indication. This method
        also calls the user callback, if any is defined.
        """
        self.queue.put({'repo_id':repo_id, 'action': action, 
                        'value':value})
        self.callback(repo_id, action, value)

    def repo_metadata(self, repo_id, value):
        """ Update the status of metadata creation. """
        self.send(repo_id, 'repo_metadata', value)

    def repo_init(self, repo_id, numpkgs):
        """ Share the total packages in a repository, when known. """
        self.send(repo_id, 'repo_init', numpkgs)

    def repo_complete(self, repo_id):
        """ Called when a repository completes downloading all packages. """
        self.send(repo_id, 'repo_complete')

    def repo_error(self, repo_id, error):
        """ Called when a repository throws an exception. """
        self.send(repo_id, 'repo_error', error)
