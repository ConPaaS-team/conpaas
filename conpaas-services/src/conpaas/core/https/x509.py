#!/usr/bin/python
"""
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
"""

"""Management of X.509 certificates using pyOpenSSL"""

from OpenSSL import crypto

def gen_rsa_keypair():
    pkey = crypto.PKey()
    pkey.generate_key(crypto.TYPE_RSA, 2048)
    return pkey

def create_x509_req(pub_key, **name):
    """
        Creates an x509 CSR. We only need to certify that the owner
        of this certificate is allowed to access the machines of
        user <<userid>>, encoded in the field CN from the
        Subject area.
    """
    req = crypto.X509Req()
    subj = req.get_subject()

    for key, value in name.items():
        setattr(subj, key, value)
    
    req.set_pubkey(pub_key)
    req.sign(pub_key, 'sha1')
    return req

def x509_req_as_pem(x509_req):
    return crypto.dump_certificate_request(crypto.FILETYPE_PEM, x509_req)

def key_as_pem(key):
    return crypto.dump_privatekey(crypto.FILETYPE_PEM, key)

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
    x509_req = create_x509_req(req_key, userId='3', serviceLocator='101',
                               O='ConPaaS', emailAddress='info@conpaas.eu',
                               CN='ConPaaS', role='agent')
    print x509_req_as_pem(x509_req)
