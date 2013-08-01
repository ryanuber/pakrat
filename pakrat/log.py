def write(message):
    print message

def debug(message):
    write('debug: %s' % message)

def trace(message):
    ''' Don't do anything for now. '''
    pass

def info(message):
    write('info: %s' % message)
