import os
import random

from OpenSSL import crypto

import common
common.extend_path()

from conpaas.core.misc import file_get_contents

def gen_rsa_keypair():
    pkey = crypto.PKey()
    pkey.generate_key(crypto.TYPE_RSA, 2048)
    return pkey
    
def create_x509_req(req_key, uid, sid, org, email, cn, role):
    req = crypto.X509Req()
    subj = req.get_subject()

    subj.O = org
    subj.CN = cn
    subj.emailAddress = email
    subj.userId = uid
    subj.serviceLocator = sid
    subj.role = role

    req.set_pubkey(req_key)
    req.sign(req_key, "md5")
    return req

def create_x509_cert(cert_dir, x509_req):
    # Load the CA cert
    ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, 
        file_get_contents(os.path.join(cert_dir, "ca_cert.pem")))
    
    # Load private key
    key = crypto.load_privatekey(crypto.FILETYPE_PEM, 
        file_get_contents(os.path.join(cert_dir, "ca_key.pem")))

    # Create new certificate
    newcert = crypto.X509()

    # Generate serial number
    serial = random.randint(1, 2048)
    newcert.set_serial_number(serial)
    
    # Valid for one year starting from now 
    newcert.gmtime_adj_notAfter(60 * 60 * 24 * 365)
    newcert.gmtime_adj_notBefore(0)

    # Issuer, subject and public key
    newcert.set_issuer(ca_cert.get_subject())
    newcert.set_subject(x509_req.get_subject())
    newcert.set_pubkey(x509_req.get_pubkey())

    # Sign
    newcert.sign(key, "md5")

    return crypto.dump_certificate(crypto.FILETYPE_PEM, newcert)

def generate_certificate(cert_dir, uid, sid, role, email, cn, org):
    """Generates a new x509 certificate for a manager from scratch.

    Creates a key, a request and then the certificate."""

    # Get CA cert
    ca_cert = file_get_contents(os.path.join(cert_dir, "ca_cert.pem"))

    # Generate keypair
    req_key  = gen_rsa_keypair()

    # Generate certificate request
    x509_req = create_x509_req(req_key, uid, sid, org, email, cn, role)

    # Sign the request
    certificate = create_x509_cert(cert_dir, x509_req)

    return { 'ca_cert': ca_cert, 
             'key': crypto.dump_privatekey(crypto.FILETYPE_PEM, req_key), 
             'cert': certificate }
