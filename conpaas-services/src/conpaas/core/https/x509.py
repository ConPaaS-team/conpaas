# -*- coding: utf-8 -*-

"""
    conpaas.core.https.x509
    =======================

    ConPaaS core: X.509 certificates handling.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

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

def create_cert(req, issuer_cert, issuer_key, serial, not_before, not_after):
    cert = crypto.X509()
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(not_before)
    cert.gmtime_adj_notAfter(not_after)
    cert.set_issuer(issuer_cert.get_subject())
    cert.set_subject(req.get_subject())
    cert.set_pubkey(req.get_pubkey())
    cert.sign(issuer_key, 'sha1')
    return cert

def x509_req_as_pem(x509_req):
    return crypto.dump_certificate_request(crypto.FILETYPE_PEM, x509_req)

def cert_as_pem(cert):
    return crypto.dump_certificate(crypto.FILETYPE_PEM, cert)

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
