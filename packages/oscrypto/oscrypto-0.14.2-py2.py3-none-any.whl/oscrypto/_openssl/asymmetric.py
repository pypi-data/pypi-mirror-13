# coding: utf-8
from __future__ import unicode_literals, division, absolute_import, print_function

import hashlib

import asn1crypto.keys
import asn1crypto.x509

from .._errors import pretty_message
from .._ffi import (
    buffer_from_bytes,
    buffer_pointer,
    bytes_from_buffer,
    deref,
    is_null,
    new,
    null,
    unwrap,
)
from ._libcrypto import libcrypto, LibcryptoConst, libcrypto_version_info, handle_openssl_error
from ..keys import parse_public, parse_certificate, parse_private, parse_pkcs12
from ..errors import AsymmetricKeyError, IncompleteAsymmetricKeyError, SignatureError
from .._types import type_name, str_cls, byte_cls
from ..util import constant_compare


__all__ = [
    'Certificate',
    'dsa_sign',
    'dsa_verify',
    'ecdsa_sign',
    'ecdsa_verify',
    'generate_pair',
    'load_certificate',
    'load_pkcs12',
    'load_private_key',
    'load_public_key',
    'PrivateKey',
    'PublicKey',
    'rsa_oaep_decrypt',
    'rsa_oaep_encrypt',
    'rsa_pkcs1v15_decrypt',
    'rsa_pkcs1v15_encrypt',
    'rsa_pkcs1v15_sign',
    'rsa_pkcs1v15_verify',
    'rsa_pss_sign',
    'rsa_pss_verify',
]


class PrivateKey():
    """
    Container for the OpenSSL representation of a private key
    """

    evp_pkey = None
    asn1 = None

    def __init__(self, evp_pkey, asn1):
        """
        :param evp_pkey:
            An OpenSSL EVP_PKEY value from loading/importing the key

        :param asn1:
            An asn1crypto.keys.PrivateKeyInfo object
        """

        self.evp_pkey = evp_pkey
        self.asn1 = asn1

    @property
    def algorithm(self):
        """
        :return:
            A unicode string of "rsa", "dsa" or "ec"
        """

        return self.asn1.algorithm

    @property
    def curve(self):
        """
        :return:
            A unicode string of EC curve name
        """

        return self.asn1.curve[1]

    @property
    def bit_size(self):
        """
        :return:
            The number of bits in the key, as an integer
        """

        return self.asn1.bit_size

    @property
    def byte_size(self):
        """
        :return:
            The number of bytes in the key, as an integer
        """

        return self.asn1.byte_size

    def __del__(self):
        if self.evp_pkey:
            libcrypto.EVP_PKEY_free(self.evp_pkey)
            self.evp_pkey = None


class PublicKey(PrivateKey):
    """
    Container for the OpenSSL representation of a public key
    """

    def __init__(self, evp_pkey, asn1):
        """
        :param evp_pkey:
            An OpenSSL EVP_PKEY value from loading/importing the key

        :param asn1:
            An asn1crypto.keys.PublicKeyInfo object
        """

        PrivateKey.__init__(self, evp_pkey, asn1)


class Certificate():
    """
    Container for the OpenSSL representation of a certificate
    """

    x509 = None
    asn1 = None
    _public_key = None
    _self_signed = None

    def __init__(self, x509, asn1):
        """
        :param x509:
            An OpenSSL X509 value from loading/importing the certificate

        :param asn1:
            An asn1crypto.x509.Certificate object
        """

        self.x509 = x509
        self.asn1 = asn1

    @property
    def algorithm(self):
        """
        :return:
            A unicode string of "rsa", "dsa" or "ec"
        """

        return self.public_key.algorithm

    @property
    def curve(self):
        """
        :return:
            A unicode string of EC curve name
        """

        return self.public_key.curve

    @property
    def bit_size(self):
        """
        :return:
            The number of bits in the public key, as an integer
        """

        return self.public_key.bit_size

    @property
    def byte_size(self):
        """
        :return:
            The number of bytes in the public key, as an integer
        """

        return self.public_key.byte_size

    @property
    def evp_pkey(self):
        """
        :return:
            The EVP_PKEY of the public key this certificate contains
        """

        return self.public_key.evp_pkey

    @property
    def public_key(self):
        """
        :return:
            The PublicKey object for the public key this certificate contains
        """

        if not self._public_key and self.x509:
            evp_pkey = libcrypto.X509_get_pubkey(self.x509)
            self._public_key = PublicKey(evp_pkey, self.asn1['tbs_certificate']['subject_public_key_info'])

        return self._public_key

    @property
    def self_signed(self):
        """
        :return:
            A boolean - if the certificate is self-signed
        """

        if self._self_signed is None:
            self._self_signed = False
            if self.asn1.self_signed in set(['yes', 'maybe']):

                signature_algo = self.asn1['signature_algorithm'].signature_algo
                hash_algo = self.asn1['signature_algorithm'].hash_algo

                if signature_algo == 'rsassa_pkcs1v15':
                    verify_func = rsa_pkcs1v15_verify
                elif signature_algo == 'dsa':
                    verify_func = dsa_verify
                elif signature_algo == 'ecdsa':
                    verify_func = ecdsa_verify
                else:
                    raise OSError(pretty_message(
                        '''
                        Unable to verify the signature of the certificate since
                        it uses the unsupported algorithm %s
                        ''',
                        signature_algo
                    ))

                try:
                    verify_func(
                        self.public_key,
                        self.asn1['signature_value'].native,
                        self.asn1['tbs_certificate'].dump(),
                        hash_algo
                    )
                    self._self_signed = True
                except (SignatureError):
                    pass

        return self._self_signed

    def __del__(self):
        if self._public_key:
            self._public_key.__del__()
            self._public_key = None

        if self.x509:
            libcrypto.X509_free(self.x509)
            self.x509 = None


def generate_pair(algorithm, bit_size=None, curve=None):
    """
    Generates a public/private key pair

    :param algorithm:
        The key algorithm - "rsa", "dsa" or "ec"

    :param bit_size:
        An integer - used for "rsa" and "dsa". For "rsa" the value maye be 1024,
        2048, 3072 or 4096. For "dsa" the value may be 1024, plus 2048 or 3072
        if OpenSSL 1.0.0 or newer is available.

    :param curve:
        A unicode string - used for "ec" keys. Valid values include "secp256r1",
        "secp384r1" and "secp521r1".

    :raises:
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library

    :return:
        A 2-element tuple of (PublicKey, PrivateKey). The contents of each key
        may be saved by calling .asn1.dump().
    """

    if algorithm not in set(['rsa', 'dsa', 'ec']):
        raise ValueError(pretty_message(
            '''
            algorithm must be one of "rsa", "dsa", "ec", not %s
            ''',
            repr(algorithm)
        ))

    if algorithm == 'rsa':
        if bit_size not in set([1024, 2048, 3072, 4096]):
            raise ValueError(pretty_message(
                '''
                bit_size must be one of 1024, 2048, 3072, 4096, not %s
                ''',
                repr(bit_size)
            ))

    elif algorithm == 'dsa':
        if libcrypto_version_info < (1,):
            if bit_size != 1024:
                raise ValueError(pretty_message(
                    '''
                    bit_size must be 1024, not %s
                    ''',
                    repr(bit_size)
                ))
        else:
            if bit_size not in set([1024, 2048, 3072]):
                raise ValueError(pretty_message(
                    '''
                    bit_size must be one of 1024, 2048, 3072, not %s
                    ''',
                    repr(bit_size)
                ))

    elif algorithm == 'ec':
        if curve not in set(['secp256r1', 'secp384r1', 'secp521r1']):
            raise ValueError(pretty_message(
                '''
                curve must be one of "secp256r1", "secp384r1", "secp521r1",
                not %s
                ''',
                repr(curve)
            ))

    if algorithm == 'rsa':
        rsa = None
        exponent = None

        try:
            rsa = libcrypto.RSA_new()
            if is_null(rsa):
                handle_openssl_error(0)

            exponent_pointer = new(libcrypto, 'BIGNUM **')
            result = libcrypto.BN_dec2bn(exponent_pointer, b'65537')
            handle_openssl_error(result)
            exponent = unwrap(exponent_pointer)

            result = libcrypto.RSA_generate_key_ex(rsa, bit_size, exponent, null())
            handle_openssl_error(result)

            buffer_length = libcrypto.i2d_RSAPublicKey(rsa, null())
            if buffer_length < 0:
                handle_openssl_error(buffer_length)
            buffer = buffer_from_bytes(buffer_length)
            result = libcrypto.i2d_RSAPublicKey(rsa, buffer_pointer(buffer))
            if result < 0:
                handle_openssl_error(result)
            public_key_bytes = bytes_from_buffer(buffer, buffer_length)

            buffer_length = libcrypto.i2d_RSAPrivateKey(rsa, null())
            if buffer_length < 0:
                handle_openssl_error(buffer_length)
            buffer = buffer_from_bytes(buffer_length)
            result = libcrypto.i2d_RSAPrivateKey(rsa, buffer_pointer(buffer))
            if result < 0:
                handle_openssl_error(result)
            private_key_bytes = bytes_from_buffer(buffer, buffer_length)

        finally:
            if rsa:
                libcrypto.RSA_free(rsa)
            if exponent:
                libcrypto.BN_free(exponent)

    elif algorithm == 'dsa':
        dsa = None

        try:
            dsa = libcrypto.DSA_new()
            if is_null(dsa):
                handle_openssl_error(0)

            result = libcrypto.DSA_generate_parameters_ex(dsa, bit_size, null(), 0, null(), null(), null())
            handle_openssl_error(result)

            result = libcrypto.DSA_generate_key(dsa)
            handle_openssl_error(result)

            buffer_length = libcrypto.i2d_DSA_PUBKEY(dsa, null())
            if buffer_length < 0:
                handle_openssl_error(buffer_length)
            buffer = buffer_from_bytes(buffer_length)
            result = libcrypto.i2d_DSA_PUBKEY(dsa, buffer_pointer(buffer))
            if result < 0:
                handle_openssl_error(result)
            public_key_bytes = bytes_from_buffer(buffer, buffer_length)

            buffer_length = libcrypto.i2d_DSAPrivateKey(dsa, null())
            if buffer_length < 0:
                handle_openssl_error(buffer_length)
            buffer = buffer_from_bytes(buffer_length)
            result = libcrypto.i2d_DSAPrivateKey(dsa, buffer_pointer(buffer))
            if result < 0:
                handle_openssl_error(result)
            private_key_bytes = bytes_from_buffer(buffer, buffer_length)

        finally:
            if dsa:
                libcrypto.DSA_free(dsa)

    elif algorithm == 'ec':
        ec_key = None

        try:
            curve_id = {
                'secp256r1': LibcryptoConst.NID_X9_62_prime256v1,
                'secp384r1': LibcryptoConst.NID_secp384r1,
                'secp521r1': LibcryptoConst.NID_secp521r1,
            }[curve]

            ec_key = libcrypto.EC_KEY_new_by_curve_name(curve_id)
            if is_null(ec_key):
                handle_openssl_error(0)

            result = libcrypto.EC_KEY_generate_key(ec_key)
            handle_openssl_error(result)

            libcrypto.EC_KEY_set_asn1_flag(ec_key, LibcryptoConst.OPENSSL_EC_NAMED_CURVE)

            buffer_length = libcrypto.i2o_ECPublicKey(ec_key, null())
            if buffer_length < 0:
                handle_openssl_error(buffer_length)
            buffer = buffer_from_bytes(buffer_length)
            result = libcrypto.i2o_ECPublicKey(ec_key, buffer_pointer(buffer))
            if result < 0:
                handle_openssl_error(result)
            public_key_point_bytes = bytes_from_buffer(buffer, buffer_length)

            # i2o_ECPublicKey only returns the ECPoint bytes, so we have to
            # manually wrap it in a PublicKeyInfo structure to get it to parse
            public_key = asn1crypto.keys.PublicKeyInfo({
                'algorithm': asn1crypto.keys.PublicKeyAlgorithm({
                    'algorithm': 'ec',
                    'parameters': asn1crypto.keys.ECDomainParameters(
                        name='named',
                        value=curve
                    )
                }),
                'public_key': public_key_point_bytes
            })
            public_key_bytes = public_key.dump()

            buffer_length = libcrypto.i2d_ECPrivateKey(ec_key, null())
            if buffer_length < 0:
                handle_openssl_error(buffer_length)
            buffer = buffer_from_bytes(buffer_length)
            result = libcrypto.i2d_ECPrivateKey(ec_key, buffer_pointer(buffer))
            if result < 0:
                handle_openssl_error(result)
            private_key_bytes = bytes_from_buffer(buffer, buffer_length)

        finally:
            if ec_key:
                libcrypto.EC_KEY_free(ec_key)

    return (load_public_key(public_key_bytes), load_private_key(private_key_bytes))

generate_pair.shimmed = False


def load_certificate(source):
    """
    Loads an x509 certificate into a Certificate object

    :param source:
        A byte string of file contents, a unicode string filename or an
        asn1crypto.x509.Certificate object

    :raises:
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library

    :return:
        A Certificate object
    """

    if isinstance(source, asn1crypto.x509.Certificate):
        certificate = source

    elif isinstance(source, byte_cls):
        certificate = parse_certificate(source)

    elif isinstance(source, str_cls):
        with open(source, 'rb') as f:
            certificate = parse_certificate(f.read())

    else:
        raise TypeError(pretty_message(
            '''
            source must be a byte string, unicode string or
            asn1crypto.x509.Certificate object, not %s
            ''',
            type_name(source)
        ))

    return _load_x509(certificate)


def _load_x509(certificate):
    """
    Loads an ASN.1 object of an x509 certificate into a Certificate object

    :param certificate:
        An asn1crypto.x509.Certificate object

    :return:
        A Certificate object
    """

    source = certificate.dump()

    buffer = buffer_from_bytes(source)
    evp_pkey = libcrypto.d2i_X509(null(), buffer_pointer(buffer), len(source))
    if is_null(evp_pkey):
        handle_openssl_error(0)
    return Certificate(evp_pkey, certificate)


def load_private_key(source, password=None):
    """
    Loads a private key into a PrivateKey object

    :param source:
        A byte string of file contents, a unicode string filename or an
        asn1crypto.keys.PrivateKeyInfo object

    :param password:
        A byte or unicode string to decrypt the private key file. Unicode
        strings will be encoded using UTF-8. Not used is the source is a
        PrivateKeyInfo object.

    :raises:
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        oscrypto.errors.AsymmetricKeyError - when the private key is incompatible with the OS crypto library
        OSError - when an error is returned by the OS crypto library

    :return:
        A PrivateKey object
    """

    if isinstance(source, asn1crypto.keys.PrivateKeyInfo):
        private_object = source

    else:
        if password is not None:
            if isinstance(password, str_cls):
                password = password.encode('utf-8')
            if not isinstance(password, byte_cls):
                raise TypeError(pretty_message(
                    '''
                    password must be a byte string, not %s
                    ''',
                    type_name(password)
                ))

        if isinstance(source, str_cls):
            with open(source, 'rb') as f:
                source = f.read()

        elif not isinstance(source, byte_cls):
            raise TypeError(pretty_message(
                '''
                source must be a byte string, unicode string or
                asn1crypto.keys.PrivateKeyInfo object, not %s
                ''',
                type_name(source)
            ))

        private_object = parse_private(source, password)

    return _load_key(private_object)


def load_public_key(source):
    """
    Loads a public key into a PublicKey object

    :param source:
        A byte string of file contents, a unicode string filename or an
        asn1crypto.keys.PublicKeyInfo object

    :raises:
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        oscrypto.errors.AsymmetricKeyError - when the public key is incompatible with the OS crypto library
        OSError - when an error is returned by the OS crypto library

    :return:
        A PublicKey object
    """

    if isinstance(source, asn1crypto.keys.PublicKeyInfo):
        public_key = source

    elif isinstance(source, byte_cls):
        public_key = parse_public(source)

    elif isinstance(source, str_cls):
        with open(source, 'rb') as f:
            public_key = parse_public(f.read())

    else:
        raise TypeError(pretty_message(
            '''
            source must be a byte string, unicode string or
            asn1crypto.keys.PublicKeyInfo object, not %s
            ''',
            type_name(public_key)
        ))

    if public_key.algorithm == 'dsa':
        if libcrypto_version_info < (1,) and public_key.hash_algo == 'sha2':
            raise AsymmetricKeyError(pretty_message(
                '''
                OpenSSL 0.9.8 only supports DSA keys based on SHA1 (2048 bits or
                less) - this key is based on SHA2 and is %s bits
                ''',
                public_key.bit_size
            ))
        elif public_key.hash_algo is None:
            raise IncompleteAsymmetricKeyError(pretty_message(
                '''
                The DSA key does not contain the necessary p, q and g
                parameters and can not be used
                '''
            ))

    data = public_key.dump()
    buffer = buffer_from_bytes(data)
    evp_pkey = libcrypto.d2i_PUBKEY(null(), buffer_pointer(buffer), len(data))
    if is_null(evp_pkey):
        handle_openssl_error(0)
    return PublicKey(evp_pkey, public_key)


def _load_key(private_object):
    """
    Loads a private key into a PrivateKey object

    :param private_object:
        An asn1crypto.keys.PrivateKeyInfo object

    :return:
        A PrivateKey object
    """

    if libcrypto_version_info < (1,) and private_object.algorithm == 'dsa' and private_object.hash_algo == 'sha2':
        raise AsymmetricKeyError(pretty_message(
            '''
            OpenSSL 0.9.8 only supports DSA keys based on SHA1 (2048 bits or
            less) - this key is based on SHA2 and is %s bits
            ''',
            private_object.bit_size
        ))

    source = private_object.unwrap().dump()

    buffer = buffer_from_bytes(source)
    evp_pkey = libcrypto.d2i_AutoPrivateKey(null(), buffer_pointer(buffer), len(source))
    if is_null(evp_pkey):
        handle_openssl_error(0)
    return PrivateKey(evp_pkey, private_object)


def load_pkcs12(source, password=None):
    """
    Loads a .p12 or .pfx file into a PrivateKey object and one or more
    Certificates objects

    :param source:
        A byte string of file contents or a unicode string filename

    :param password:
        A byte or unicode string to decrypt the PKCS12 file. Unicode strings
        will be encoded using UTF-8.

    :raises:
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        oscrypto.errors.AsymmetricKeyError - when a contained key is incompatible with the OS crypto library
        OSError - when an error is returned by the OS crypto library

    :return:
        A three-element tuple containing (PrivateKey, Certificate, [Certificate, ...])
    """

    if password is not None:
        if isinstance(password, str_cls):
            password = password.encode('utf-8')
        if not isinstance(password, byte_cls):
            raise TypeError(pretty_message(
                '''
                password must be a byte string, not %s
                ''',
                type_name(password)
            ))

    if isinstance(source, str_cls):
        with open(source, 'rb') as f:
            source = f.read()

    elif not isinstance(source, byte_cls):
        raise TypeError(pretty_message(
            '''
            source must be a byte string or a unicode string, not %s
            ''',
            type_name(source)
        ))

    key_info, cert_info, extra_certs_info = parse_pkcs12(source, password)

    key = None
    cert = None

    if key_info:
        key = _load_key(key_info)

    if cert_info:
        cert = _load_x509(cert_info)

    extra_certs = [_load_x509(info) for info in extra_certs_info]

    return (key, cert, extra_certs)


def rsa_pkcs1v15_encrypt(certificate_or_public_key, data):
    """
    Encrypts a byte string using an RSA public key or certificate. Uses PKCS#1
    v1.5 padding.

    :param certificate_or_public_key:
        A PublicKey or Certificate object

    :param data:
        A byte string, with a maximum length 11 bytes less than the key length
        (in bytes)

    :raises:
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library

    :return:
        A byte string of the encrypted data
    """

    return _encrypt(certificate_or_public_key, data, LibcryptoConst.RSA_PKCS1_PADDING)


def rsa_pkcs1v15_decrypt(private_key, ciphertext):
    """
    Decrypts a byte string using an RSA private key. Uses PKCS#1 v1.5 padding.

    :param private_key:
        A PrivateKey object

    :param ciphertext:
        A byte string of the encrypted data

    :raises:
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library

    :return:
        A byte string of the original plaintext
    """

    return _decrypt(private_key, ciphertext, LibcryptoConst.RSA_PKCS1_PADDING)


def rsa_oaep_encrypt(certificate_or_public_key, data):
    """
    Encrypts a byte string using an RSA public key or certificate. Uses PKCS#1
    OAEP padding with SHA1.

    :param certificate_or_public_key:
        A PublicKey or Certificate object

    :param data:
        A byte string, with a maximum length 41 bytes (or more) less than the
        key length (in bytes)

    :raises:
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library

    :return:
        A byte string of the encrypted data
    """

    return _encrypt(certificate_or_public_key, data, LibcryptoConst.RSA_PKCS1_OAEP_PADDING)


def rsa_oaep_decrypt(private_key, ciphertext):
    """
    Decrypts a byte string using an RSA private key. Uses PKCS#1 OAEP padding
    with SHA1.

    :param private_key:
        A PrivateKey object

    :param ciphertext:
        A byte string of the encrypted data

    :raises:
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library

    :return:
        A byte string of the original plaintext
    """

    return _decrypt(private_key, ciphertext, LibcryptoConst.RSA_PKCS1_OAEP_PADDING)


def _encrypt(certificate_or_public_key, data, padding):
    """
    Encrypts plaintext using an RSA public key or certificate

    :param certificate_or_public_key:
        A PublicKey, Certificate or PrivateKey object

    :param data:
        The byte string to encrypt

    :param padding:
        The padding mode to use

    :raises:
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library

    :return:
        A byte string of the encrypted data
    """

    if not isinstance(certificate_or_public_key, (Certificate, PublicKey)):
        raise TypeError(pretty_message(
            '''
            certificate_or_public_key must be an instance of the Certificate or
            PublicKey class, not %s
            ''',
            type_name(certificate_or_public_key)
        ))

    if not isinstance(data, byte_cls):
        raise TypeError(pretty_message(
            '''
            data must be a byte string, not %s
            ''',
            type_name(data)
        ))

    rsa = None

    try:
        buffer_size = libcrypto.EVP_PKEY_size(certificate_or_public_key.evp_pkey)
        buffer = buffer_from_bytes(buffer_size)

        rsa = libcrypto.EVP_PKEY_get1_RSA(certificate_or_public_key.evp_pkey)
        res = libcrypto.RSA_public_encrypt(len(data), data, buffer, rsa, padding)
        handle_openssl_error(res)

        return bytes_from_buffer(buffer, res)

    finally:
        if rsa:
            libcrypto.RSA_free(rsa)


def _decrypt(private_key, ciphertext, padding):
    """
    Decrypts RSA ciphertext using a private key

    :param private_key:
        A PrivateKey object

    :param ciphertext:
        The ciphertext - a byte string

    :param padding:
        The padding mode to use

    :raises:
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library

    :return:
        A byte string of the plaintext
    """

    if not isinstance(private_key, PrivateKey):
        raise TypeError(pretty_message(
            '''
            private_key must be an instance of the PrivateKey class, not %s
            ''',
            type_name(private_key)
        ))

    if not isinstance(ciphertext, byte_cls):
        raise TypeError(pretty_message(
            '''
            ciphertext must be a byte string, not %s
            ''',
            type_name(ciphertext)
        ))

    rsa = None

    try:
        buffer_size = libcrypto.EVP_PKEY_size(private_key.evp_pkey)
        buffer = buffer_from_bytes(buffer_size)

        rsa = libcrypto.EVP_PKEY_get1_RSA(private_key.evp_pkey)
        res = libcrypto.RSA_private_decrypt(len(ciphertext), ciphertext, buffer, rsa, padding)
        handle_openssl_error(res)

        return bytes_from_buffer(buffer, res)

    finally:
        if rsa:
            libcrypto.RSA_free(rsa)


def rsa_pkcs1v15_verify(certificate_or_public_key, signature, data, hash_algorithm):
    """
    Verifies an RSASSA-PKCS-v1.5 signature.

    When the hash_algorithm is "raw", the operation is identical to RSA
    public key decryption. That is: the data is not hashed and no ASN.1
    structure with an algorithm identifier of the hash algorithm is placed in
    the encrypted byte string.

    :param certificate_or_public_key:
        A Certificate or PublicKey instance to verify the signature with

    :param signature:
        A byte string of the signature to verify

    :param data:
        A byte string of the data the signature is for

    :param hash_algorithm:
        A unicode string of "md5", "sha1", "sha224", "sha256", "sha384",
        "sha512" or "raw"

    :raises:
        oscrypto.errors.SignatureError - when the signature is determined to be invalid
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library
    """

    if certificate_or_public_key.algorithm != 'rsa':
        raise ValueError(pretty_message(
            '''
            The key specified is not an RSA public key, but %s
            ''',
            certificate_or_public_key.algorithm.upper()
        ))

    return _verify(certificate_or_public_key, signature, data, hash_algorithm)


def rsa_pss_verify(certificate_or_public_key, signature, data, hash_algorithm):
    """
    Verifies an RSASSA-PSS signature. For the PSS padding the mask gen algorithm
    will be mgf1 using the same hash algorithm as the signature. The salt length
    with be the length of the hash algorithm, and the trailer field with be the
    standard 0xBC byte.

    :param certificate_or_public_key:
        A Certificate or PublicKey instance to verify the signature with

    :param signature:
        A byte string of the signature to verify

    :param data:
        A byte string of the data the signature is for

    :param hash_algorithm:
        A unicode string of "md5", "sha1", "sha224", "sha256", "sha384" or "sha512"

    :raises:
        oscrypto.errors.SignatureError - when the signature is determined to be invalid
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library
    """

    if certificate_or_public_key.algorithm != 'rsa':
        raise ValueError(pretty_message(
            '''
            The key specified is not an RSA public key, but %s
            ''',
            certificate_or_public_key.algorithm.upper()
        ))

    return _verify(certificate_or_public_key, signature, data, hash_algorithm, rsa_pss_padding=True)


def dsa_verify(certificate_or_public_key, signature, data, hash_algorithm):
    """
    Verifies a DSA signature

    :param certificate_or_public_key:
        A Certificate or PublicKey instance to verify the signature with

    :param signature:
        A byte string of the signature to verify

    :param data:
        A byte string of the data the signature is for

    :param hash_algorithm:
        A unicode string of "md5", "sha1", "sha224", "sha256", "sha384" or "sha512"

    :raises:
        oscrypto.errors.SignatureError - when the signature is determined to be invalid
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library
    """

    if certificate_or_public_key.algorithm != 'dsa':
        raise ValueError(pretty_message(
            '''
            The key specified is not a DSA public key, but %s
            ''',
            certificate_or_public_key.algorithm.upper()
        ))

    return _verify(certificate_or_public_key, signature, data, hash_algorithm)


def ecdsa_verify(certificate_or_public_key, signature, data, hash_algorithm):
    """
    Verifies an ECDSA signature

    :param certificate_or_public_key:
        A Certificate or PublicKey instance to verify the signature with

    :param signature:
        A byte string of the signature to verify

    :param data:
        A byte string of the data the signature is for

    :param hash_algorithm:
        A unicode string of "md5", "sha1", "sha224", "sha256", "sha384" or "sha512"

    :raises:
        oscrypto.errors.SignatureError - when the signature is determined to be invalid
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library
    """

    if certificate_or_public_key.algorithm != 'ec':
        raise ValueError(pretty_message(
            '''
            The key specified is not an EC public key, but %s
            ''',
            certificate_or_public_key.algorithm.upper()
        ))

    return _verify(certificate_or_public_key, signature, data, hash_algorithm)


def _verify(certificate_or_public_key, signature, data, hash_algorithm, rsa_pss_padding=False):
    """
    Verifies an RSA, DSA or ECDSA signature

    :param certificate_or_public_key:
        A Certificate or PublicKey instance to verify the signature with

    :param signature:
        A byte string of the signature to verify

    :param data:
        A byte string of the data the signature is for

    :param hash_algorithm:
        A unicode string of "md5", "sha1", "sha224", "sha256", "sha384" or "sha512"

    :param rsa_pss_padding:
        If the certificate_or_public_key is an RSA key, this enables PSS padding

    :raises:
        oscrypto.errors.SignatureError - when the signature is determined to be invalid
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library
    """

    if not isinstance(certificate_or_public_key, (Certificate, PublicKey)):
        raise TypeError(pretty_message(
            '''
            certificate_or_public_key must be an instance of the Certificate or
            PublicKey class, not %s
            ''',
            type_name(certificate_or_public_key)
        ))

    if not isinstance(signature, byte_cls):
        raise TypeError(pretty_message(
            '''
            signature must be a byte string, not %s
            ''',
            type_name(signature)
        ))

    if not isinstance(data, byte_cls):
        raise TypeError(pretty_message(
            '''
            data must be a byte string, not %s
            ''',
            type_name(data)
        ))

    valid_hash_algorithms = set(['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512'])
    if certificate_or_public_key.algorithm == 'rsa' and not rsa_pss_padding:
        valid_hash_algorithms |= set(['raw'])

    if hash_algorithm not in valid_hash_algorithms:
        valid_hash_algorithms_error = '"md5", "sha1", "sha224", "sha256", "sha384", "sha512"'
        if certificate_or_public_key.algorithm == 'rsa' and not rsa_pss_padding:
            valid_hash_algorithms_error += ', "raw"'
        raise ValueError(pretty_message(
            '''
            hash_algorithm must be one of %s, not %s
            ''',
            valid_hash_algorithms_error,
            repr(hash_algorithm)
        ))

    if certificate_or_public_key.algorithm != 'rsa' and rsa_pss_padding:
        raise ValueError(pretty_message(
            '''
            PSS padding can only be used with RSA keys - the key provided is a
            %s key
            ''',
            certificate_or_public_key.algorithm.upper()
        ))

    if certificate_or_public_key.algorithm == 'rsa' and hash_algorithm == 'raw':
        if len(data) > certificate_or_public_key.byte_size - 11:
            raise ValueError(pretty_message(
                '''
                data must be 11 bytes shorter than the key size when
                hash_algorithm is "raw" - key size is %s bytes, but data is
                %s bytes long
                ''',
                certificate_or_public_key.byte_size,
                len(data)
            ))

        rsa = None

        try:
            rsa = libcrypto.EVP_PKEY_get1_RSA(certificate_or_public_key.evp_pkey)
            if is_null(rsa):
                handle_openssl_error(0)

            buffer_size = libcrypto.EVP_PKEY_size(certificate_or_public_key.evp_pkey)
            decrypted_buffer = buffer_from_bytes(buffer_size)
            decrypted_length = libcrypto.RSA_public_decrypt(
                len(signature),
                signature,
                decrypted_buffer,
                rsa,
                LibcryptoConst.RSA_PKCS1_PADDING
            )
            handle_openssl_error(decrypted_length)

            decrypted_bytes = bytes_from_buffer(decrypted_buffer, decrypted_length)

            if not constant_compare(data, decrypted_bytes):
                raise SignatureError('Signature is invalid')
            return

        finally:
            if rsa:
                libcrypto.RSA_free(rsa)

    evp_md_ctx = None
    rsa = None
    dsa = None
    dsa_sig = None
    ec_key = None
    ecdsa_sig = None

    try:
        evp_md_ctx = libcrypto.EVP_MD_CTX_create()

        evp_md = {
            'md5': libcrypto.EVP_md5,
            'sha1': libcrypto.EVP_sha1,
            'sha224': libcrypto.EVP_sha224,
            'sha256': libcrypto.EVP_sha256,
            'sha384': libcrypto.EVP_sha384,
            'sha512': libcrypto.EVP_sha512
        }[hash_algorithm]()

        if libcrypto_version_info < (1,):
            if certificate_or_public_key.algorithm == 'rsa' and rsa_pss_padding:
                digest = getattr(hashlib, hash_algorithm)(data).digest()

                rsa = libcrypto.EVP_PKEY_get1_RSA(certificate_or_public_key.evp_pkey)
                if is_null(rsa):
                    handle_openssl_error(0)

                buffer_size = libcrypto.EVP_PKEY_size(certificate_or_public_key.evp_pkey)
                decoded_buffer = buffer_from_bytes(buffer_size)
                decoded_length = libcrypto.RSA_public_decrypt(
                    len(signature),
                    signature,
                    decoded_buffer,
                    rsa,
                    LibcryptoConst.RSA_NO_PADDING
                )
                handle_openssl_error(decoded_length)

                res = libcrypto.RSA_verify_PKCS1_PSS(
                    rsa,
                    digest,
                    evp_md,
                    decoded_buffer,
                    LibcryptoConst.EVP_MD_CTX_FLAG_PSS_MDLEN
                )

            elif certificate_or_public_key.algorithm == 'rsa':
                res = libcrypto.EVP_DigestInit_ex(evp_md_ctx, evp_md, null())
                handle_openssl_error(res)

                res = libcrypto.EVP_DigestUpdate(evp_md_ctx, data, len(data))
                handle_openssl_error(res)

                res = libcrypto.EVP_VerifyFinal(
                    evp_md_ctx,
                    signature,
                    len(signature),
                    certificate_or_public_key.evp_pkey
                )

            elif certificate_or_public_key.algorithm == 'dsa':
                digest = getattr(hashlib, hash_algorithm)(data).digest()

                signature_buffer = buffer_from_bytes(signature)
                signature_pointer = buffer_pointer(signature_buffer)
                dsa_sig = libcrypto.d2i_DSA_SIG(null(), signature_pointer, len(signature))
                if is_null(dsa_sig):
                    handle_openssl_error(0)

                dsa = libcrypto.EVP_PKEY_get1_DSA(certificate_or_public_key.evp_pkey)
                if is_null(dsa):
                    handle_openssl_error(0)

                res = libcrypto.DSA_do_verify(digest, len(digest), dsa_sig, dsa)

            elif certificate_or_public_key.algorithm == 'ec':
                digest = getattr(hashlib, hash_algorithm)(data).digest()

                signature_buffer = buffer_from_bytes(signature)
                signature_pointer = buffer_pointer(signature_buffer)
                ecdsa_sig = libcrypto.d2i_ECDSA_SIG(null(), signature_pointer, len(signature))
                if is_null(ecdsa_sig):
                    handle_openssl_error(0)

                ec_key = libcrypto.EVP_PKEY_get1_EC_KEY(certificate_or_public_key.evp_pkey)
                if is_null(ec_key):
                    handle_openssl_error(0)

                res = libcrypto.ECDSA_do_verify(digest, len(digest), ecdsa_sig, ec_key)

        else:
            evp_pkey_ctx_pointer_pointer = new(libcrypto, 'EVP_PKEY_CTX **')
            res = libcrypto.EVP_DigestVerifyInit(
                evp_md_ctx,
                evp_pkey_ctx_pointer_pointer,
                evp_md,
                null(),
                certificate_or_public_key.evp_pkey
            )
            handle_openssl_error(res)
            evp_pkey_ctx_pointer = unwrap(evp_pkey_ctx_pointer_pointer)

            if rsa_pss_padding:
                # Enable PSS padding
                res = libcrypto.EVP_PKEY_CTX_ctrl(
                    evp_pkey_ctx_pointer,
                    LibcryptoConst.EVP_PKEY_RSA,
                    -1,  # All operations
                    LibcryptoConst.EVP_PKEY_CTRL_RSA_PADDING,
                    LibcryptoConst.RSA_PKCS1_PSS_PADDING,
                    null()
                )
                handle_openssl_error(res)

                # Use the hash algorithm output length as the salt length
                res = libcrypto.EVP_PKEY_CTX_ctrl(
                    evp_pkey_ctx_pointer,
                    LibcryptoConst.EVP_PKEY_RSA,
                    LibcryptoConst.EVP_PKEY_OP_SIGN | LibcryptoConst.EVP_PKEY_OP_VERIFY,
                    LibcryptoConst.EVP_PKEY_CTRL_RSA_PSS_SALTLEN,
                    -1,
                    null()
                )
                handle_openssl_error(res)

            res = libcrypto.EVP_DigestUpdate(evp_md_ctx, data, len(data))
            handle_openssl_error(res)

            res = libcrypto.EVP_DigestVerifyFinal(evp_md_ctx, signature, len(signature))

        if res < 1:
            raise SignatureError('Signature is invalid')
        handle_openssl_error(res)

    finally:
        if evp_md_ctx:
            libcrypto.EVP_MD_CTX_destroy(evp_md_ctx)
        if rsa:
            libcrypto.RSA_free(rsa)
        if dsa:
            libcrypto.DSA_free(dsa)
        if dsa_sig:
            libcrypto.DSA_SIG_free(dsa_sig)
        if ec_key:
            libcrypto.EC_KEY_free(ec_key)
        if ecdsa_sig:
            libcrypto.ECDSA_SIG_free(ecdsa_sig)


def rsa_pkcs1v15_sign(private_key, data, hash_algorithm):
    """
    Generates an RSASSA-PKCS-v1.5 signature.

    When the hash_algorithm is "raw", the operation is identical to RSA
    private key encryption. That is: the data is not hashed and no ASN.1
    structure with an algorithm identifier of the hash algorithm is placed in
    the encrypted byte string.

    :param private_key:
        The PrivateKey to generate the signature with

    :param data:
        A byte string of the data the signature is for

    :param hash_algorithm:
        A unicode string of "md5", "sha1", "sha224", "sha256", "sha384",
        "sha512" or "raw"

    :raises:
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library

    :return:
        A byte string of the signature
    """

    if private_key.algorithm != 'rsa':
        raise ValueError(pretty_message(
            '''
            The key specified is not an RSA private key, but %s
            ''',
            private_key.algorithm.upper()
        ))

    return _sign(private_key, data, hash_algorithm)


def rsa_pss_sign(private_key, data, hash_algorithm):
    """
    Generates an RSASSA-PSS signature. For the PSS padding the mask gen
    algorithm will be mgf1 using the same hash algorithm as the signature. The
    salt length with be the length of the hash algorithm, and the trailer field
    with be the standard 0xBC byte.

    :param private_key:
        The PrivateKey to generate the signature with

    :param data:
        A byte string of the data the signature is for

    :param hash_algorithm:
        A unicode string of "md5", "sha1", "sha224", "sha256", "sha384" or "sha512"

    :raises:
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library

    :return:
        A byte string of the signature
    """

    if private_key.algorithm != 'rsa':
        raise ValueError(pretty_message(
            '''
            The key specified is not an RSA private key, but %s
            ''',
            private_key.algorithm.upper()
        ))

    return _sign(private_key, data, hash_algorithm, rsa_pss_padding=True)


def dsa_sign(private_key, data, hash_algorithm):
    """
    Generates a DSA signature

    :param private_key:
        The PrivateKey to generate the signature with

    :param data:
        A byte string of the data the signature is for

    :param hash_algorithm:
        A unicode string of "md5", "sha1", "sha224", "sha256", "sha384" or "sha512"

    :raises:
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library

    :return:
        A byte string of the signature
    """

    if private_key.algorithm != 'dsa':
        raise ValueError(pretty_message(
            '''
            The key specified is not a DSA private key, but %s
            ''',
            private_key.algorithm.upper()
        ))

    return _sign(private_key, data, hash_algorithm)


def ecdsa_sign(private_key, data, hash_algorithm):
    """
    Generates an ECDSA signature

    :param private_key:
        The PrivateKey to generate the signature with

    :param data:
        A byte string of the data the signature is for

    :param hash_algorithm:
        A unicode string of "md5", "sha1", "sha224", "sha256", "sha384" or "sha512"

    :raises:
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library

    :return:
        A byte string of the signature
    """

    if private_key.algorithm != 'ec':
        raise ValueError(pretty_message(
            '''
            The key specified is not an EC private key, but %s
            ''',
            private_key.algorithm.upper()
        ))

    return _sign(private_key, data, hash_algorithm)


def _sign(private_key, data, hash_algorithm, rsa_pss_padding=False):
    """
    Generates an RSA, DSA or ECDSA signature

    :param private_key:
        The PrivateKey to generate the signature with

    :param data:
        A byte string of the data the signature is for

    :param hash_algorithm:
        A unicode string of "md5", "sha1", "sha224", "sha256", "sha384" or "sha512"

    :param rsa_pss_padding:
        If the private_key is an RSA key, this enables PSS padding

    :raises:
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by the OS crypto library

    :return:
        A byte string of the signature
    """

    if not isinstance(private_key, PrivateKey):
        raise TypeError(pretty_message(
            '''
            private_key must be an instance of PrivateKey, not %s
            ''',
            type_name(private_key)
        ))

    if not isinstance(data, byte_cls):
        raise TypeError(pretty_message(
            '''
            data must be a byte string, not %s
            ''',
            type_name(data)
        ))

    valid_hash_algorithms = set(['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512'])
    if private_key.algorithm == 'rsa' and not rsa_pss_padding:
        valid_hash_algorithms |= set(['raw'])

    if hash_algorithm not in valid_hash_algorithms:
        valid_hash_algorithms_error = '"md5", "sha1", "sha224", "sha256", "sha384", "sha512"'
        if private_key.algorithm == 'rsa' and not rsa_pss_padding:
            valid_hash_algorithms_error += ', "raw"'
        raise ValueError(pretty_message(
            '''
            hash_algorithm must be one of %s, not %s
            ''',
            valid_hash_algorithms_error,
            repr(hash_algorithm)
        ))

    if private_key.algorithm != 'rsa' and rsa_pss_padding:
        raise ValueError(pretty_message(
            '''
            PSS padding can only be used with RSA keys - the key provided is a
            %s key
            ''',
            private_key.algorithm.upper()
        ))

    if private_key.algorithm == 'rsa' and hash_algorithm == 'raw':
        if len(data) > private_key.byte_size - 11:
            raise ValueError(pretty_message(
                '''
                data must be 11 bytes shorter than the key size when
                hash_algorithm is "raw" - key size is %s bytes, but data is
                %s bytes long
                ''',
                private_key.byte_size,
                len(data)
            ))

        rsa = None

        try:
            rsa = libcrypto.EVP_PKEY_get1_RSA(private_key.evp_pkey)
            if is_null(rsa):
                handle_openssl_error(0)

            buffer_size = libcrypto.EVP_PKEY_size(private_key.evp_pkey)

            signature_buffer = buffer_from_bytes(buffer_size)
            signature_length = libcrypto.RSA_private_encrypt(
                len(data),
                data,
                signature_buffer,
                rsa,
                LibcryptoConst.RSA_PKCS1_PADDING
            )
            handle_openssl_error(signature_length)

            return bytes_from_buffer(signature_buffer, signature_length)

        finally:
            if rsa:
                libcrypto.RSA_free(rsa)

    evp_md_ctx = None
    rsa = None
    dsa = None
    dsa_sig = None
    ec_key = None
    ecdsa_sig = None

    try:
        evp_md_ctx = libcrypto.EVP_MD_CTX_create()

        evp_md = {
            'md5': libcrypto.EVP_md5,
            'sha1': libcrypto.EVP_sha1,
            'sha224': libcrypto.EVP_sha224,
            'sha256': libcrypto.EVP_sha256,
            'sha384': libcrypto.EVP_sha384,
            'sha512': libcrypto.EVP_sha512
        }[hash_algorithm]()

        if libcrypto_version_info < (1,):
            if private_key.algorithm == 'rsa' and rsa_pss_padding:
                digest = getattr(hashlib, hash_algorithm)(data).digest()

                rsa = libcrypto.EVP_PKEY_get1_RSA(private_key.evp_pkey)
                if is_null(rsa):
                    handle_openssl_error(0)

                buffer_size = libcrypto.EVP_PKEY_size(private_key.evp_pkey)
                em_buffer = buffer_from_bytes(buffer_size)
                res = libcrypto.RSA_padding_add_PKCS1_PSS(
                    rsa,
                    em_buffer,
                    digest,
                    evp_md,
                    LibcryptoConst.EVP_MD_CTX_FLAG_PSS_MDLEN
                )
                handle_openssl_error(res)

                signature_buffer = buffer_from_bytes(buffer_size)
                signature_length = libcrypto.RSA_private_encrypt(
                    buffer_size,
                    em_buffer,
                    signature_buffer,
                    rsa,
                    LibcryptoConst.RSA_NO_PADDING
                )
                handle_openssl_error(signature_length)

            elif private_key.algorithm == 'rsa':
                buffer_size = libcrypto.EVP_PKEY_size(private_key.evp_pkey)
                signature_buffer = buffer_from_bytes(buffer_size)
                signature_length = new(libcrypto, 'unsigned int *')

                res = libcrypto.EVP_DigestInit_ex(evp_md_ctx, evp_md, null())
                handle_openssl_error(res)

                res = libcrypto.EVP_DigestUpdate(evp_md_ctx, data, len(data))
                handle_openssl_error(res)

                res = libcrypto.EVP_SignFinal(
                    evp_md_ctx,
                    signature_buffer,
                    signature_length,
                    private_key.evp_pkey
                )
                handle_openssl_error(res)

                signature_length = deref(signature_length)

            elif private_key.algorithm == 'dsa':
                digest = getattr(hashlib, hash_algorithm)(data).digest()

                dsa = libcrypto.EVP_PKEY_get1_DSA(private_key.evp_pkey)
                if is_null(dsa):
                    handle_openssl_error(0)

                dsa_sig = libcrypto.DSA_do_sign(digest, len(digest), dsa)
                if is_null(dsa_sig):
                    handle_openssl_error(0)

                buffer_size = libcrypto.i2d_DSA_SIG(dsa_sig, null())
                signature_buffer = buffer_from_bytes(buffer_size)
                signature_pointer = buffer_pointer(signature_buffer)
                signature_length = libcrypto.i2d_DSA_SIG(dsa_sig, signature_pointer)
                handle_openssl_error(signature_length)

            elif private_key.algorithm == 'ec':
                digest = getattr(hashlib, hash_algorithm)(data).digest()

                ec_key = libcrypto.EVP_PKEY_get1_EC_KEY(private_key.evp_pkey)
                if is_null(ec_key):
                    handle_openssl_error(0)

                ecdsa_sig = libcrypto.ECDSA_do_sign(digest, len(digest), ec_key)
                if is_null(ecdsa_sig):
                    handle_openssl_error(0)

                buffer_size = libcrypto.i2d_ECDSA_SIG(ecdsa_sig, null())
                signature_buffer = buffer_from_bytes(buffer_size)
                signature_pointer = buffer_pointer(signature_buffer)
                signature_length = libcrypto.i2d_ECDSA_SIG(ecdsa_sig, signature_pointer)
                handle_openssl_error(signature_length)

        else:
            buffer_size = libcrypto.EVP_PKEY_size(private_key.evp_pkey)
            signature_buffer = buffer_from_bytes(buffer_size)
            signature_length = new(libcrypto, 'size_t *', buffer_size)

            evp_pkey_ctx_pointer_pointer = new(libcrypto, 'EVP_PKEY_CTX **')
            res = libcrypto.EVP_DigestSignInit(
                evp_md_ctx,
                evp_pkey_ctx_pointer_pointer,
                evp_md,
                null(),
                private_key.evp_pkey
            )
            handle_openssl_error(res)
            evp_pkey_ctx_pointer = unwrap(evp_pkey_ctx_pointer_pointer)

            if rsa_pss_padding:
                # Enable PSS padding
                res = libcrypto.EVP_PKEY_CTX_ctrl(
                    evp_pkey_ctx_pointer,
                    LibcryptoConst.EVP_PKEY_RSA,
                    -1,  # All operations
                    LibcryptoConst.EVP_PKEY_CTRL_RSA_PADDING,
                    LibcryptoConst.RSA_PKCS1_PSS_PADDING,
                    null()
                )
                handle_openssl_error(res)

                # Use the hash algorithm output length as the salt length
                res = libcrypto.EVP_PKEY_CTX_ctrl(
                    evp_pkey_ctx_pointer,
                    LibcryptoConst.EVP_PKEY_RSA,
                    LibcryptoConst.EVP_PKEY_OP_SIGN | LibcryptoConst.EVP_PKEY_OP_VERIFY,
                    LibcryptoConst.EVP_PKEY_CTRL_RSA_PSS_SALTLEN,
                    -1,
                    null()
                )
                handle_openssl_error(res)

            res = libcrypto.EVP_DigestUpdate(evp_md_ctx, data, len(data))
            handle_openssl_error(res)

            res = libcrypto.EVP_DigestSignFinal(evp_md_ctx, signature_buffer, signature_length)
            handle_openssl_error(res)

            signature_length = deref(signature_length)

        return bytes_from_buffer(signature_buffer, signature_length)

    finally:
        if evp_md_ctx:
            libcrypto.EVP_MD_CTX_destroy(evp_md_ctx)
        if rsa:
            libcrypto.RSA_free(rsa)
        if dsa:
            libcrypto.DSA_free(dsa)
        if dsa_sig:
            libcrypto.DSA_SIG_free(dsa_sig)
        if ec_key:
            libcrypto.EC_KEY_free(ec_key)
        if ecdsa_sig:
            libcrypto.ECDSA_SIG_free(ecdsa_sig)
