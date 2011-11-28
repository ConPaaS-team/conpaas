'''
Created on Feb 8, 2011

@author: ielhelw
'''

import re, zipfile, tarfile, socket

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
  except:
    raise ValueError('Invalid IP string')

def verify_ip_port_list(l):
  '''Check l is a list of [IP, PORT]. Raise appropriate Error if invalid types
  or values were found
  '''
  if type(l) != list:
    raise TypeError('Expected a list of [IP, PORT]')
  for pair in l:
    if len(pair) != 2:
      raise TypeError('List should contain IP,PORT values')
    verify_ip_or_domain(pair[0])
    verify_port(pair[1])

zip = ['.zip']
tar = ['.tar', '.tar.gz', '.tar.bz2']

def archive_supported_extensions():
  return tar + zip

def archive_supported_name(name):
  for ext in tar + zip:
    if name.endswith(ext):
      return True
  return False

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
