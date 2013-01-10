#!/usr/bin/env python

from cpsdirector import common, db

from conpaas.core.https import x509

import os
import sys
import random
import platform

from distutils.spawn import find_executable

CERT_DIR = common.config.get('conpaas', 'CERT_DIR')
hostname = common.rlinput('Please enter your hostname: ', platform.node())

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

open('/etc/apache2/sites-available/conpaas-director', 'w').write(conf)

conffile = open(common.CONFFILE).read()
if 'DIRECTOR_URL' not in conffile:
    # append DIRECTOR_URL
    open(common.CONFFILE, 'a').write("\nDIRECTOR_URL = https://%s:%s" % (hostname, conf_values['port']))

db.create_all()

confdir = common.config.get('conpaas', 'CONF_DIR')
common.chown(os.path.join(confdir, 'director.db'), 'www-data', 'www-data')
