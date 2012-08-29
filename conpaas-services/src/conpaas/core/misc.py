'''
Copyright (c) 2010-2012, Contrail consortium.
All rights reserved.

Redistribution and use in source and binary forms, 
with or without modification, are permitted provided
that the following conditions are met:

 1. Redistributions of source code must retain the
    above copyright notice, this list of conditions
    and the following disclaimer.
 2. Redistributions in binary form must reproduce
    the above copyright notice, this list of 
    conditions and the following disclaimer in the
    documentation and/or other materials provided
    with the distribution.
 3. Neither the name of the Contrail consortium nor the
    names of its contributors may be used to endorse
    or promote products derived from this software 
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.


Created on Feb 8, 2011

@author: ielhelw
'''

import zipfile, tarfile, socket, fcntl, struct


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
