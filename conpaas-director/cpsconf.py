#!/usr/bin/env python

from cpsdirector import common, db

from conpaas.core.https import x509
from conpaas.core.misc import rlinput

import os
import re
import sys
import random
import platform

from urlparse import urlparse
from distutils.spawn import find_executable

CERT_DIR = common.config_parser.get('conpaas', 'CERT_DIR')

if common.config_parser.has_option('director', 'DIRECTOR_URL'):
    # Get default hostname from DIRECTOR_URL if it exists already
    hostname = common.config_parser.get('director', 'DIRECTOR_URL')
    hostname = re.sub(':.*', '', urlparse(hostname).netloc)
else:
    # If DIRECTOR_URL does not exist, just trust platform.node()
    hostname = platform.node()

try:
    hostname = sys.argv[1]
except IndexError:
    hostname = rlinput('Please enter your hostname: ', hostname)

# create CA keypair
cakey = x509.gen_rsa_keypair()

# save ca_key.pem to filesystem
open(os.path.join(CERT_DIR, 'ca_key.pem'), 'w').write(x509.key_as_pem(cakey))

# create cert request
req = x509.create_x509_req(cakey, CN='CA', emailAddress='info@conpaas.eu',
                           O='ConPaaS')

five_years = 60 * 60 * 24 * 365 * 5

# create ca certificate, valid for five years
cacert = x509.create_cert(
    req=req,
    issuer_cert=req,
    issuer_key=cakey,
    serial=random.randint(1, sys.maxint),
    not_before=0,
    not_after=five_years)

# save ca_cert.pem to filesystem
open(os.path.join(CERT_DIR, 'ca_cert.pem'), 'w').write(
    x509.cert_as_pem(cacert))

# create director key
dkey = x509.gen_rsa_keypair()

# save key.pem to filesystem
open(os.path.join(CERT_DIR, 'key.pem'), 'w').write(x509.key_as_pem(dkey))

# create director cert request
req = x509.create_x509_req(dkey, CN=hostname, emailAddress='info@conpaas.eu',
                           O='ConPaaS', role='frontend')

# create director certificate
dcert = x509.create_cert(
    req=req,
    issuer_cert=cacert,
    issuer_key=cakey,
    serial=random.randint(1, sys.maxint),
    not_before=0,
    not_after=five_years)

# save cert.pem to filesystem
open(os.path.join(CERT_DIR, 'cert.pem'), 'w').write(x509.cert_as_pem(dcert))

# find director.wsgi absolute path. We have to chdir or it will return the
# relative one
os.chdir('/')
wsgi_exec = find_executable('director.wsgi')

# create apache config file
conf_values = {
    'hostname': hostname,
    'wsgi':     wsgi_exec,
    'wsgidir':  os.path.dirname(wsgi_exec),
    'port':     5555
}

conf = """
Listen %(port)s
<VirtualHost *:%(port)s>
    ServerName %(hostname)s

    WSGIDaemonProcess director user=www-data group=www-data threads=5
    WSGIScriptAlias / %(wsgi)s

    <Directory %(wsgidir)s>
        WSGIProcessGroup director
""" % conf_values

conf += """
        WSGIApplicationGroup %{GLOBAL}
        WSGIPassApacheRequest On

        SSLRequireSSL
        SSLVerifyClient optional
        SSLVerifyDepth 2
        SSLOptions +StdEnvVars +ExportCertData

        Order deny,allow
        Allow from all
    </Directory>

    SSLEngine on

    SSLCertificateFile    /etc/cpsdirector/certs/cert.pem
    SSLCertificateKeyFile /etc/cpsdirector/certs/key.pem

    SSLCACertificateFile  /etc/cpsdirector/certs/ca_cert.pem

    CustomLog ${APACHE_LOG_DIR}/director-access.log combined
    ErrorLog ${APACHE_LOG_DIR}/director-error.log
</VirtualHost>
"""

try:
    open('/etc/apache2/sites-available/conpaas-director', 'w').write(conf)
except IOError:
    print "W: Cannot write Apache config file. Are you root?"
    sys.exit(0)

conflines = open(common.CONFFILE).readlines()

director_url = "DIRECTOR_URL = https://%s:%s\n" % (hostname, conf_values['port'])

try:
    num, line = [ (num, line) for num, line in enumerate(conflines) 
        if 'DIRECTOR_URL' in line ][0]
    # DIRECTOR_URL already there. Update its value.
    conflines[num] = director_url
except IndexError:
    # DIRECTOR_URL is not present. Add it.
    conflines.append(director_url)

open(common.CONFFILE, 'w').writelines(conflines)

db.create_all()

confdir = common.config_parser.get('conpaas', 'CONF_DIR')
common.chown(os.path.join(confdir, 'director.db'), 'www-data', 'www-data')
