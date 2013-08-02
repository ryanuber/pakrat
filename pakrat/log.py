def write(message):
    print message

def debug(message):
    write('debug: %s' % message)

def trace(message):
    ''' Don't do anything for now. '''
    pass

def error(message):
    write('error: %s' % message)

def info(message):
    write('info: %s' % message)
