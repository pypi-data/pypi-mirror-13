# Copyright (c) 2013 Yubico AB
# All rights reserved.
#
#   Redistribution and use in source and binary forms, with or
#   without modification, are permitted provided that the following
#   conditions are met:
#
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, rsa, padding
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.x509.oid import NameOID

from base64 import urlsafe_b64decode, urlsafe_b64encode
from hashlib import sha256
import os

PUB_KEY_DER_PREFIX = "3059301306072a8648ce3d020106082a8648ce3d030107034200" \
    .decode('hex')


def certificate_from_der(der):
    return x509.load_der_x509_certificate(der, default_backend())


def subject_from_certificate(cert):
    return cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value


def pub_key_from_der(der):
    return load_der_public_key(PUB_KEY_DER_PREFIX + der, default_backend())


def websafe_decode(data):
    if isinstance(data, unicode):
        data = data.encode('utf-8')
    data += '=' * (-len(data) % 4)
    return urlsafe_b64decode(data)


def websafe_encode(data):
    return urlsafe_b64encode(data).replace('=', '')


def sha_256(data):
    h = sha256()
    h.update(data)
    return h.digest()


def rand_bytes(n_bytes):
    return os.urandom(n_bytes)


def verify_ecdsa_signature(payload, pubkey, signature):
    verifier = pubkey.verifier(signature, ec.ECDSA(hashes.SHA256()))
    verifier.update(payload)

    verifier.verify()


def verify_cert_signature(cert, pubkey):
    cert_signature = cert.signature
    cert_bytes = cert.tbs_certificate_bytes

    if isinstance(pubkey, rsa.RSAPublicKey):
        verifier = pubkey.verifier(
            cert_signature,
            padding.PKCS1v15(),
            cert.signature_hash_algorithm
        )
    elif isinstance(pubkey, ec.EllipticCurvePublicKey):
        verifier = pubkey.verifier(
            cert_signature,
            ec.ECDSA(cert.signature_hash_algorithm)
        )
    else:
        raise ValueError("Unsupported public key value")

    verifier.update(cert_bytes)

    try:
        verifier.verify()
        return True
    except InvalidSignature:
        return False
