#!/usr/bin/python
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


Created on June, 2012

@author aaasz
@file

'''

""" 
    Management of X.509 certificates

    It uses the python-m2crypto library o create X509 certificate
    requests which will be sent to the CA. 

    It also uses the python-openssl library to parse certificates.
   
    TODO: rewrite all using the python-openssl library
"""



import M2Crypto
from OpenSSL import crypto

def gen_rsa_keypair():
    key_pair = M2Crypto.RSA.gen_key(2048, 65537)
    key = M2Crypto.EVP.PKey(md='sha1')
    key.assign_rsa(key_pair)
    return key

def create_x509_req(pub_key, userid, serviceid, org, email, cn, role):
    """
        Creates an x509 CSR. We only need to certify that the owner
        of this certificate is allowed to access the machines of
        user <<userid>>, encoded in the field CN from the
        Subject area.
    """
    def _add_field(key, value):
        req_name.add_entry_by_txt(field=key,
                                  type=M2Crypto.ASN1.MBSTRING_ASC,
                                  entry=value,
                                  len=-1, loc=-1, set=0)

    x509_req = M2Crypto.X509.Request()
    req_name = M2Crypto.X509.X509_Name()

    _add_field('O', org)
    _add_field('CN', cn)
    _add_field('emailAddress', email)
    _add_field('userId', userid)
    _add_field('serviceLocator', serviceid)
    _add_field('role', role)

    x509_req.set_subject_name(req_name)
    x509_req.set_pubkey(pkey=pub_key)
    x509_req.sign(pub_key, md='sha1' )
    
    return x509_req

def get_x509_dn_field(cert, field):
    """
        Returns the requested field from the distinguished name  of
        the given certificate
        
        @param cert a string representing the certificate in PEM format

        @return a string representing the value of the requested field
    """
    x509_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
    components = x509_cert.get_subject().get_components()
    for (key, value) in components:
        if key == field:
            return value
    return None


if __name__ == '__main__':
    req_key = gen_rsa_keypair()
    x509_req = create_x509_req(req_key, '3', '101',
                               'ConPaaS', 'info@conpaas.eu',
                               'ConPaaS', 'agent')
    print x509_req.as_text()
