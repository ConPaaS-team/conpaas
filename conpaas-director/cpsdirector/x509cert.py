import os
import random

from OpenSSL import crypto

from conpaas.core.misc import file_get_contents
from conpaas.core.https import x509

def create_x509_cert(cert_dir, x509_req):
    # Load the CA cert
    ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, 
        file_get_contents(os.path.join(cert_dir, "ca_cert.pem")))
    
    # Load private key
    key = crypto.load_privatekey(crypto.FILETYPE_PEM, 
        file_get_contents(os.path.join(cert_dir, "ca_key.pem")))

    # Generate serial number
    serial = random.randint(1, 2048)

    # Valid for one year starting from now 
    not_before = 0
    not_after  = 60 * 60 * 24 * 365

    newcert = x509.create_cert(x509_req, 
        ca_cert, key, serial, not_before, not_after)

    return crypto.dump_certificate(crypto.FILETYPE_PEM, newcert)

def generate_certificate(cert_dir, uid, sid, role, email, cn, org, ca_cert=None):
    """Generates a new x509 certificate for a manager from scratch.

    Creates a key, a request and then the certificate."""

    # Get CA cert
    if ca_cert is None:
        ca_cert = file_get_contents(os.path.join(cert_dir, "ca_cert.pem"))

    # Generate keypair
    req_key  = x509.gen_rsa_keypair()

    # Generate certificate request
    x509_req = x509.create_x509_req(req_key, userId=uid, serviceLocator=sid, 
        O=org, emailAddress=email, CN=cn, role=role)

    # Sign the request
    certificate = create_x509_cert(cert_dir, x509_req)

    return { 'ca_cert': ca_cert, 
             'key': crypto.dump_privatekey(crypto.FILETYPE_PEM, req_key), 
             'cert': certificate }
