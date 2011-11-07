import os

def valid_file(file):
    if not os.path.exists(file):
        raise ValueError('File "%s" does not exist' % file)
    
    return file
