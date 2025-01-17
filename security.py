import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import dh, rsa
from cryptography.exceptions import InvalidSignature
import secrets
from cryptography.hazmat.primitives import hashes, padding, serialization, hmac
from cryptography.hazmat.backends import default_backend
import base64
#from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import random
import pickle
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

### First we generate a shared secret using DH, after that we apply KDF that will result in a shared key.
### Then we use that shared key in AES.

####### Diffie Hellman from cryptography.hazmat.primitives #######

class DiffieHellman:

    def __init__(self, p, g):
        self.private_key = None
        self.public_key = None
        self.shared_key = None
        self.p = p
        self.g = g
        self.parameters = dh.DHParameterNumbers(self.p, self.g).parameters(backend=default_backend())
        self.getExchangeKeys()

    def getExchangeKeys(self):
        self.private_key = self.parameters.generate_private_key()
        self.public_key = base64.b64encode(self.private_key.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo))

    def getSharedKey(self, peer_public_key):
        print(peer_public_key)
        pub = serialization.load_der_public_key(base64.b64decode(peer_public_key), backend=default_backend())
        shared_secret = self.private_key.exchange(pub)


        # Key derivation
        self.shared_key = HKDF(algorithm=hashes.SHA256(),
                            length=32,
                            salt=None,
                            info=b'handshake data',
                            backend=default_backend()
                        ).derive(shared_secret)


####### Diffie Hellman Key Exchange Algorithm made by us #######

# class DiffieHellman:
#     prime = 103079
#     generator = 7

#     def __init__(self):
#         self.secret_value = random.randint(1,100)
#         self.public_value = self.generate_pk()

#     def generate_pk(self):
#         public_value = (self.generator ** self.secret_value) % self.prime
#         return public_value

#     def generate_ss(self, secret_value, other_key):
#         shared_secret = (other_key ** self.secret_value) % self.prime
#         return shared_secret

#     def __str__(self):
#         return "secret values is " + str(self.secret_value) + " and public value is " + str(self.public_value)

### test ###
# alice = DiffieHellman()
# bob = DiffieHellman()

# alice_ss = alice.generate_ss(alice.secret_value, bob.public_value)
# print(alice_ss)
# bob_ss = bob.generate_ss(bob.secret_value, alice.public_value)
# print(bob_ss)


########### Key Derivation (KDF) ############

# def keyDerivation(key):


#     kdf = PBKDF2HMAC(
#         hashes.SHA512(), 32, bytes(5), 10000, default_backend()
#     )
#     key = kdf.derive(bytes(key))

#     return key

########### Cifra simétrica usando AESGCM ############


class SymmetricCipher:

    def encrypt_message(self, message, key):

        IV = os.urandom(algorithms.AES.block_size // 8)
        cipher = Cipher(
            algorithms.AES(key), 
            modes.CBC(IV), 
            default_backend()
        )
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()

        padded = padder.update(message) + padder.finalize()
        ciphertext = encryptor.update(padded) + encryptor.finalize()

        return base64.b64encode(IV + ciphertext).decode('utf-8')

    def decrypt_message(self, ciphertext, key):

        c = base64.b64decode(ciphertext.encode('utf-8'))

        IV, ciphertext_text = c[:algorithms.AES.block_size//8], c[algorithms.AES.block_size//8:]
        cipher = Cipher(
            algorithms.AES(key), 
            modes.CBC(IV), 
            default_backend()
        )
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

        pt = decryptor.update(ciphertext_text) + decryptor.finalize()
        plaintext = unpadder.update(pt) + unpadder.finalize()

        return plaintext


#### HMAC: Hashed Message Authentication Code #### 

class HMAC():

    def hmac_update(self, key, msg):

        if not isinstance(msg, bytes):
            msg = pickle.dumps(msg)

        h = hmac.HMAC(b"key", hashes.SHA256(), backend=default_backend())
        h.update(msg)
        print(h)

        return h.finalize()

    def hmac_verify(self, key, hmac_msg, msg):

        if not isinstance(msg, bytes):
            msg = pickle.dumps(msg)

        h = hmac.HMAC(b"key", hashes.SHA256(), backend=default_backend())
        h.update(msg)
        return h.verify(hmac_msg)

#### RSA ####

# class RSA():

#     def __init__(self):
#         self.private_key = None
#         self.public_key = None
#         self.generateKeys()

#     def generateKeys(self):
#         self.private_key = rsa.generate_private_key(
#                             public_exponent=65537,
#                             key_size=2048,
#                             backend=default_backend()
#                             )
#         self.public_key = self.private_key.public_key()

#         return self.private_key, self.public_key

#     def asym_encrypt(self, msg, key):
#         enc_msg = key.encrypt(
#                     msg,
#                     padding.OAEP(
#                         mgf=padding.MGF1(algorithm=hashes.SHA256()),
#                         algorithm=hashes.SHA256(),
#                         label=None
#                     )
#         )

#         return enc_msg

#     def asym_decrypt(self, msg, key):
#         dec_msg = key.decrypt(
#                     msg,
#                     padding.OAEP(
#                         mgf=padding.MGF1(algorithm=hashes.SHA256()),
#                         algorithm=hashes.SHA256(),
#                         label=None
#                     )       
#         )
#         return dec_msg

#     def signature(self, msg, key):
#         sign = key.sign(
#                     msg,
#                     padding.PSS(
#                         mgf=padding.MGF1(hashes.SHA256()),
#                         salt_length=padding.PSS.MAX_LENGTH
#                     ),
#                     hashes.SHA256()
#         )

#         return sign

#     def verifySignature(self, msg, key, sign):
#         try:
#             key.verify(
#                     sign,
#                     msg,
#                     padding.PSS(
#                         mgf=padding.MGF1(hashes.SHA256()),
#                         salt_length=padding.PSS.MAX_LENGTH
#                     ),
#                     hashes.SHA256()
#             )
#         except InvalidSignature:
#             return False