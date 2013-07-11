import socket
import fcntl
import struct
import zipfile
import tarfile
import readline

from subprocess import Popen, PIPE

def file_get_contents(filepath):
    f = open(filepath, 'r')
    filecontent = f.read()
    f.close()
    return filecontent

def verify_port(port):
    '''Raise Type Error if port is not an integer.
    Raise ValueError if port is an invlid integer value.
    '''
    if type(port) != int: raise TypeError('port should be an integer')
    if port < 1 or port > 65535: raise ValueError('port should be a valid port number')

def verify_ip_or_domain(ip):
    '''Raise TypeError f ip is not a string.
    Raise ValueError if ip is an invalid IP address in dot notation.
    '''
    if (type(ip) != str and type(ip) != unicode):
        raise TypeError('IP is should be a string')
    try:
        socket.gethostbyname(ip)
    except Exception as e:
        raise ValueError('Invalid IP string "%s" -- %s' % (ip, e))

def verify_ip_port_list(l):
    '''Check l is a list of [IP, PORT]. Raise appropriate Error if invalid types
    or values were found
    '''
    if type(l) != list:
        raise TypeError('Expected a list of [IP, PORT]')
    for pair in l:
        if len(pair) != 2:
            raise TypeError('List should contain IP,PORT values')
        if 'ip' not in pair or 'port' not in pair:
            raise TypeError('List should contain IP,PORT values')
        verify_ip_or_domain(pair['ip'])
        verify_port(pair['port'])

def archive_get_type(name):
    if tarfile.is_tarfile(name):
        return 'tar'
    elif zipfile.is_zipfile(name):
        return 'zip'
    else: return None

def archive_open(name):
    if tarfile.is_tarfile(name):
        return tarfile.open(name)
    elif zipfile.is_zipfile(name):
        return zipfile.ZipFile(name)
    else: return None

def archive_get_members(arch):
    if isinstance(arch, zipfile.ZipFile):
        members = arch.namelist()
    elif isinstance(arch, tarfile.TarFile):
        members = [ i.name for i in arch.getmembers() ]
    return members

def archive_extract(arch, path):
    if isinstance(arch, zipfile.ZipFile):
        arch.extractall(path)
    elif isinstance(arch, tarfile.TarFile):
        arch.extractall(path=path)

def archive_close(arch):
    if isinstance(arch, zipfile.ZipFile)\
    or isinstance(arch, tarfile.TarFile):
        arch.close()

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def run_cmd(cmd, directory='/'):
    pipe = Popen(cmd, shell=True, cwd=directory, stdout=PIPE, stderr=PIPE)
    out, error = pipe.communicate()
    pipe.wait()
    return out, error

def rlinput(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return raw_input(prompt)
    finally:
        readline.set_startup_hook()

def list_lines(lines):
    """Returns the list of trimmed lines.
    
    @param lines  Multi-line string
    
    """
    return list(filter(None, (x.strip() for x in lines.splitlines())))

