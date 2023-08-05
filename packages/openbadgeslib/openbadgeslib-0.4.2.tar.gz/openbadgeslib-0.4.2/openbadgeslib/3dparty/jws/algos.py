import re

from .exceptions import SignatureError, RouteMissingError, RouteEndpointError

class AlgorithmBase(object):
    """Base for algorithm support classes."""
    pass

class HasherBase(AlgorithmBase):
    """
    Base for algos which need a hash function. The ``bits`` param can be
    passed in from the capturing group of the routing regexp
    """
    supported_bits = (256, 384, 512)
    def __init__(self, bits):
        """
        Determine if the algorithm supports the requested bit depth and set up
        matching hash method from ``hashlib`` if necessary.
        """
        self.bits = int(bits)
        if self.bits not in self.supported_bits:
            raise NotImplementedError("%s implements %s bit algorithms (given %d)" %
                                      (self.__class__, ', '.join(self.supported_bits), self.bits))
        if not getattr(self, 'hasher', None):
            import hashlib
            self.hasher = getattr(hashlib, 'sha%d' % self.bits)

class HMAC(HasherBase):
    """
    Support for HMAC signing.
    """
    def sign(self, msg, key):
        import hmac
        return hmac.new(key, msg, self.hasher).digest()

    def verify(self, msg, crypto, key):
        if not self.sign(msg, key) == crypto:
            raise SignatureError("Could not validate signature")
        return True

class RSABase(HasherBase):
    """
    Support for RSA signing.

    The ``Crypto`` package is required. However...

    NOTE: THIS ALGORITHM IS CRIPPLED AND INCOMPLETE

    Section 7.2 of the specification (found at
    http://self-issued.info/docs/draft-jones-json-web-signature.html)
    describes the algorithm for creating a JWS with RSA. It is mandatory to
    use RSASSA-PKCS1-V1_5-SIGN and either SHA256, 385 or 512.

    Problem 1: The Crypto library doesn't currently support PKCS1-V1_5. There
    is a fork that does have support:

    https://github.com/Legrandin/pycrypto/tree/pkcs1

    Problem 2: The PKCS signing method requires a Crypto.Hash class.
    Crypto.Hash doesn't yet have support anything above SHA256.

    Bottom line, you should probably use ECDSA instead.
    """
    supported_bits = (256,384,512,) #:Seems to worka > 256

    def __init__(self, padder, bits):
        super(RSABase,self).__init__(bits)
        self.padder = padder
        from Crypto.Hash import SHA256,SHA384,SHA512
        self.hashm = __import__('Crypto.Hash.SHA%d'%self.bits, globals(), locals(), ['*']).new()

    def sign(self, msg, key):
        """
        Signs a message with an RSA PrivateKey and hash method
        """
        import Crypto.PublicKey.RSA as RSA

        self.hashm.update(msg)
        ## assume we are dealing with a real key
        # private_key = RSA.importKey(key)
        return self.padder.new(key).sign(self.hashm)             # pycrypto 2.5

    def verify(self, msg, crypto, key):
        """
        Verifies a message using RSA cryptographic signature and key.

        ``crypto`` is the cryptographic signature
        ``key`` is the verifying key. Can be a real key object or a string.
        """
        import Crypto.PublicKey.RSA as RSA

        self.hashm.update(msg)
        private_key = key
        if not isinstance(key, RSA._RSAobj):
            private_key = RSA.importKey(key)
        if not self.padder.new( private_key ).verify(self.hashm,  crypto):  #:pycrypto 2.5
            raise SignatureError("Could not validate signature")
        return True

class RSA_PKCS1_5(RSABase):
    def __init__(self, bits):
        import Crypto.Signature.PKCS1_v1_5 as PKCS
        super(RSA_PKCS1_5,self).__init__(PKCS, bits)

class RSA_PSS(RSABase):
    def __init__(self, bits):
        import Crypto.Signature.PKCS1_PSS as PSS
        super(RSA_PSS,self).__init__(PSS, bits)

class ECDSA(HasherBase):
    """
    Support for ECDSA signing. This is the preferred algorithm for private/public key
    verification.

    The ``ecdsa`` package is required. ``pip install ecdsa``
    """
    bits_to_curve = {
        256: 'NIST256p',
        384: 'NIST384p',
        512: 'NIST521p',
    }
    def sign(self, msg, key):
        """
        Signs a message with an ECDSA SigningKey and hash method matching the
        bit depth of curve algorithm.
        """
        import ecdsa
        ##  assume the signing key is already a real key
        # curve = getattr(ecdsa, self.bits_to_curve[self.bits])
        # signing_key = ecdsa.SigningKey.from_string(key, curve=curve)
        # signing_key = ecdsa.SigningKey.from_string(key, curve=curve)
        return key.sign_deterministic(msg, hashfunc=self.hasher, sigencode=ecdsa.util.sigencode_der)

    def verify(self, msg, crypto, key):
        """
        Verifies a message using ECDSA cryptographic signature and key.
ecdsa signture encapsulation
        ``crypto`` is the cryptographic signature
        ``key`` is the verifying key. Can be a real key object or a string.
        """
        import ecdsa
        curve = getattr(ecdsa, self.bits_to_curve[self.bits])
        vk = key
        if not isinstance(vk, ecdsa.VerifyingKey):
            vk = ecdsa.VerifyingKey.from_string(key, curve=curve)
        try:
            vk.verify(crypto, msg, hashfunc=self.hasher, sigdecode=ecdsa.util.sigdecode_der)
        except ecdsa.BadSignatureError:
            raise SignatureError("Could not validate signature")
        return True

# algorithm routing
def route(name):
    return resolve(*find(name))

def find(name):
    # TODO: more error checking around custom algorithms
    algorithms = CUSTOM + list(DEFAULT)
    for (route, endpoint) in algorithms:
        match = re.match(route, name)
        if match:
            return (endpoint, match)
    raise RouteMissingError('endpoint matching %s could not be found' % name)

def resolve(endpoint, match):
    if callable(endpoint):
        # send result back through
        return resolve(endpoint(**match.groupdict()), match)

    # get the sign and verify methods from dict or obj
    try:
        crypt = { 'sign': endpoint['sign'], 'verify': endpoint['verify'] }
    except TypeError:
        try:
            crypt = { 'sign': endpoint.sign, 'verify': endpoint.verify }
        except AttributeError:
            raise RouteEndpointError('route enpoint must have sign, verify as attributes or items of dict')
    # verify callability
    try:
        assert callable(crypt['sign'])
        assert callable(crypt['verify'])
    except AssertionError:
        raise RouteEndpointError('sign, verify of endpoint must be callable')
    return crypt

DEFAULT = (
    (r'^HS(?P<bits>256|384|512)$', HMAC),
    (r'^RS(?P<bits>256|384|512)$', RSA_PKCS1_5),
    (r'^PS(?P<bits>256|384|512)$', RSA_PSS),
    (r'^ES(?P<bits>256|384|512)$', ECDSA),
)
CUSTOM = []
