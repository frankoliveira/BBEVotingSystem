from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from typing import Union
import base64
DEFAULT_RSA_PUBLIC_EXPONENT = 65537
DEFAULT_RSA_KEY_SIZE = 2048
DEFAULT_RSA_ENCRYPTION_PADDING = padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
DEFAULT_RSA_SIGN_PADDING = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)

class CustomRSA:
    '''
    RSA (Rivest-Shamir-Adleman)
    A cryptographic class to perform RSA operations.
    '''

    @staticmethod
    def new_keys():
        private_key = rsa.generate_private_key(public_exponent=DEFAULT_RSA_PUBLIC_EXPONENT, key_size=DEFAULT_RSA_KEY_SIZE)
        public_key = private_key.public_key()
        return private_key, public_key
    
    @staticmethod
    def save_pem_private_key(private_key: rsa.RSAPrivateKey, path: str):
        pem_private_key = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        with open(path, 'wb') as file:
            file.write(pem_private_key)
            file.close()

    @staticmethod
    def save_pem_public_key(public_key: rsa.RSAPublicKey, path: str):
        pem_public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.PKCS1
        )

        with open(path, 'wb') as file:
            file.write(pem_public_key)
            file.close()
    
    @staticmethod
    def load_pem_private_key_from_file(path: str) -> rsa.RSAPrivateKey:
        try:
            with open(path, 'rb') as file:
                private_key = serialization.load_pem_private_key(data = file.read(), 
                                                password=None, 
                                                backend=default_backend())
                return private_key
            
        except Exception as ex:
            raise Exception(f'Failed to load private key: {ex}')

    @staticmethod
    def load_pem_public_key_from_file(path: str) -> rsa.RSAPublicKey:
        try:
            with open(path, 'rb') as file:
                public_key = serialization.load_pem_public_key(
                    data = file.read(), 
                    backend = default_backend())
                return public_key
            
        except Exception as ex:
            raise Exception('Failed to load public key from file.')
        
    @staticmethod
    def load_pem_public_key_from_bytes(key: bytes) -> rsa.RSAPublicKey:
        try:
            public_key = serialization.load_pem_public_key(
                data = key, 
                backend = default_backend())
            return public_key
            
        except Exception as ex:
            raise Exception('Failed to load public key from bytes.')

    @staticmethod
    def decrypt(private_key: rsa.RSAPrivateKey, cipher_text: bytes) -> bytes:
        try:
            plain_data = private_key.decrypt(ciphertext = cipher_text, 
                                          padding = DEFAULT_RSA_ENCRYPTION_PADDING)
            return plain_data
        
        except Exception as ex:
            raise Exception('Failed to decrypt.')
    
    @staticmethod
    def encrypt(public_key: rsa.RSAPublicKey, plain_text: bytes) -> bytes:
        try:
            cipher_data = public_key.encrypt(plaintext = plain_text, 
                                             padding = DEFAULT_RSA_ENCRYPTION_PADDING)
            return cipher_data
        
        except Exception as ex:
            raise Exception('Failed to encrypt.')
        
    @staticmethod
    def sign(private_key: rsa.RSAPrivateKey, message: bytes):
        try:
            signature = private_key.sign(
                data=message,
                padding=DEFAULT_RSA_SIGN_PADDING,
                algorithm=hashes.SHA256()
            )
            return signature
        
        except Exception as ex:
            raise Exception('Failed to sign.')
        
    def verify(public_key: rsa.RSAPublicKey, signature: bytes, message: bytes):
        try:
            public_key.verify(
                            signature=signature,
                            data=message,
                            padding=DEFAULT_RSA_SIGN_PADDING,
                            algorithm=hashes.SHA256()
                        )
            return True
        except InvalidSignature as ex:
            return False
        except Exception as ex:
            raise Exception('Failed to verify.') 

        
"""#DEMOSTRAÇÃO RSA
priv_key = rsa.generate_private_key(public_exponent=65537, key_size=1024)
CustomRSA.save_pem_private_key(private_key=priv_key, path='./private_key.pem')
CustomRSA.save_pem_public_key(public_key=priv_key.public_key(), path='./public_key.pem')

public_key = CustomRSA.load_pem_public_key_from_file('./public_key.pem')
print(f'rsa n: {public_key.public_numbers().n}')
print(f'rsa e: {public_key.public_numbers().e}')

private_key = CustomRSA.load_pem_private_key_from_file('./private_key.pem')

msg = 'Informacão secreta'
msg_encoded = msg.encode('utf-8')
enc_msg = CustomRSA.encrypt(public_key=public_key, plain_text=msg_encoded)
dec_msg = CustomRSA.decrypt(private_key=private_key, cipher_text=enc_msg)
print(f'mensagem descriptada: {dec_msg.decode("utf-8")}')

sign = CustomRSA.sign(private_key=private_key,
                      message=msg_encoded)
print('original sign', sign)
sign_hex_str = sign.hex()
print('sign hex str: ', sign_hex_str)
sign_bytes = bytes.fromhex(sign_hex_str)
print('sign from hex str: ', sign_bytes)

verification = CustomRSA.verify(public_key=public_key,
                                signature=sign_bytes,
                                message=msg_encoded)
print(f'verification: {verification}')
"""

"""
#DEMOSTRAÇÃO PAILLIER
from phe import paillier, PaillierPrivateKey, PaillierPublicKey, EncryptedNumber

class PaillierHomomorphicEncryptionManager():
    def rsa_private_key_to_phe_private_key(private_key: rsa.RSAPrivateKey):
        phe_public_key = paillier.PaillierPublicKey(n=private_key.public_key().public_numbers().n)
        phe_public_key.g = private_key.public_key().public_numbers().n + 1
        phe_private_key = paillier.PaillierPrivateKey(public_key=phe_public_key,
                                    p=private_key.private_numbers().p,
                                    q=private_key.private_numbers().q)
        
        return phe_public_key, phe_private_key
    
phe_public_key, phe_private_key = PaillierHomomorphicEncryptionManager.rsa_private_key_to_phe_private_key(private_key)
sum_of_encrypted_votes = phe_public_key.encrypt(0)
for i in range(100):
    cipher_vote  = phe_public_key.encrypt(1)
    sum_of_encrypted_votes = sum_of_encrypted_votes + cipher_vote
print(f'encrypted sum of votes: {sum_of_encrypted_votes.ciphertext()}\n')

result = phe_private_key.decrypt(sum_of_encrypted_votes)
print(f'decrypted sum of votes: {result}')

paillier.generate_paillier_keypair()
"""