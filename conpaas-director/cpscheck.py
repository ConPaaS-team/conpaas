#!/usr/bin/env python

import re
import sys
from urlparse import urlparse

from cpsdirector import x509cert, common

cname = x509cert.get_cert_cname(common.config_parser.get(
    'conpaas', 'CERT_DIR'))

director_url = common.config_parser.get('director', 'DIRECTOR_URL')
director_hostname = re.sub(':.*', '', urlparse(director_url).netloc)

if cname != director_hostname:
    print >> sys.stderr, "E: The hostname part of DIRECTOR_URL (%s) does not match the cname found in %s/cert.pem (%s)" % (
        director_hostname, common.config_parser.get('conpaas', 'CERT_DIR'), cname)
else:
    print >> sys.stderr, "OK: The hostname part of DIRECTOR_URL (%s) matches the cname found in %s/cert.pem (%s)" % (
        director_hostname, common.config_parser.get('conpaas', 'CERT_DIR'), cname)
