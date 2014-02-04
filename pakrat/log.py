import sys
import syslog

def write(pri, message):
    """ Record a log message.

    Currently just uses syslog, and if unattended, writes the log messages
    to stdout so they can be piped elsewhere.
    """
    syslog.openlog('pakrat')  # sets log ident
    syslog.syslog(pri, message)
    if not sys.stdout.isatty():
        print message  # print if running unattended

def debug(message):
    """ Record a debugging message. """
    write(syslog.LOG_DEBUG, 'debug: %s' % message)

def trace(message):
    """ Record a trace message """
    write(syslog.LOG_DEBUG, 'trace: %s' % message)

def error(message):
    """ Record an error message. """
    write(syslog.LOG_ERR, 'error: %s' % message)

def info(message):
    """ Record an informational message. """
    write(syslog.LOG_INFO, message)
