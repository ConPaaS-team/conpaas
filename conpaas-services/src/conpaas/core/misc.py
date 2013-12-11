import socket
import fcntl
import struct
import zipfile
import tarfile
import readline

from subprocess import Popen, PIPE

from conpaas.core.https.server import FileUploadField


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
        ### FIXME HECTOR ...
        #if len(pair) != 2:
        if len(pair) < 2:
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
    _return_code = pipe.wait()
    return out, error


def run_cmd_code(cmd, directory='/'):
    """Same as run_cmd but it returns also the return code.
    Parameters
    ----------
    cmd : string
        command to run in a shell
    directory : string, default to '/'
        directory where to run the command
    Returns
    -------
    std_out, std_err, return_code
        a triplet with standard output, standard error output and return code.
    std_out : string
    std_err : string
    return_code : int
    """
    pipe = Popen(cmd, shell=True, cwd=directory, stdout=PIPE, stderr=PIPE)
    out, error = pipe.communicate()
    return_code = pipe.wait()
    return out, error, return_code


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


def is_constraint(constraint, filter_res, errmsg):
    def filter_constraint(arg):
        if constraint(arg):
            return filter_res(arg)
        else:
            raise Exception(errmsg(arg))
    return filter_constraint


def is_int(argument):
    return is_constraint(lambda arg: isinstance(arg, int),
                         lambda arg: int(arg),
                         lambda arg: "'%s' is not an integer but a %s." % (arg, type(arg)))(argument)


def is_more_than(minval):
    return is_constraint(lambda arg: arg > minval,
                         lambda arg: arg,
                         lambda arg: "'%s' is not more than '%s'." % (arg, minval))


def is_more_or_eq_than(minval):
    return is_constraint(lambda arg: arg >= minval,
                         lambda arg: arg,
                         lambda arg: "'%s' is not more or equal than '%s'." % (arg, minval))


def is_pos_int(argument):
    argint = is_int(argument)
    return is_more_than(0)(argint)


def is_pos_nul_int(argument):
    argint = is_int(argument)
    return is_more_or_eq_than(0)(argint)


def is_in_list(exp_list):
    return is_constraint(lambda arg: arg in exp_list,
                         lambda arg: arg,
                         lambda arg: "'%s' must be one of '%s'." % (arg, exp_list))


def is_string(argument):
    return is_constraint(lambda arg: isinstance(arg, str) or isinstance(arg, unicode),
                         lambda arg: arg,
                         lambda arg: "'%s' is not a string but a %s." % (arg, type(arg)))(argument)


def is_list(argument):
    return is_constraint(lambda arg: isinstance(arg, list),
                         lambda arg: arg,
                         lambda arg: "'%s' is not a list but a %s." % (arg, type(arg)))(argument)


def is_dict(argument):
    return is_constraint(lambda arg: isinstance(arg, dict),
                         lambda arg: arg,
                         lambda arg: "'%s' is not a dict but a %s." % (arg, type(arg)))(argument)


def is_uploaded_file(argument):
    return is_constraint(lambda arg: isinstance(arg, FileUploadField),
                         lambda arg: arg,
                         lambda arg: "'%s' is not uploaded file but a %s." % (arg, type(arg)))(argument)


def is_dict2(mandatory_keys, optional_keys=None):
    def _dict2(argument):
        argdict = is_dict(argument)
        keys = argument.keys()
        for mand_key in mandatory_keys:
            try:
                keys.remove(mand_key)
            except:
                raise Exception("Was expecting key %s in dict %s" \
                                % (mand_key, argdict))
        if optional_keys is None:
            _optional_keys = []
        else:
            _optional_keys = optional_keys
        for opt_key in _optional_keys:
            try:
                keys.remove(opt_key)
            except:
                continue
        if len(keys) > 0:
            raise Exception("Unexpected key in dict %s: %s." % (argdict, keys))
        return argdict
    return _dict2


def is_list_dict(argument):
    mylist = is_list(argument)
    for arg in mylist:
        _dict = is_dict(arg)
    return mylist


def is_list_dict2(mandatory_keys, optional_keys=None):
    def _list_dict2(argument):
        mylist = is_list_dict(argument)
        for arg in mylist:
            _dict = is_dict2(mandatory_keys, optional_keys)(arg)
        return mylist
    return _list_dict2


def check_arguments(expected_params, args):
    """ Check, convert POST arguments provided as dict.

    Parameter
    ---------
    expected_params: list
        list of expected parameters where a parameter is a tuple
        (name, constraint)                 for mandatory argument
        (name, constraint, default_value)  for optional parameter
        where constraint is 'string', 'int', 'posint', 'posnulint', 'list'

    args: dict
        args[name] = value

    Returns
    -------
    A list of all correct and converted parameters in the same order
    as the expected_params argument.
    Or raise an exception if one of the expected arguments is not there,
    or does not respect the corresponding constraint, or was not expected.
    """
    parsed_args = []
    for param in expected_params:
        if len(param) >= 2:
            name = param[0]
            constraint = param[1]
            if name in args:
                value = args.pop(name)
                try:
                    parsed_value = constraint(value)
                    parsed_args.append(parsed_value)
                except Exception as ex:
                    raise Exception("Parameter '%s': %s." % (name, ex))
            else:
                if len(param) >= 3:
                    default_value = param[2]
                    # TODO: decide whether the default value should satisfy the constraint
                    parsed_args.append(default_value)
                else:
                    raise Exception("Missing the mandatory parameter %s." % name)
        else:
            raise Exception("Unexpected number of arguments describing a parameter: %s" % param)
    if len(args) > 0:
        raise Exception("Unexpected parameters: %s." % args)
    if len(parsed_args) == 1:
        return parsed_args[0]
    else:
        return parsed_args
