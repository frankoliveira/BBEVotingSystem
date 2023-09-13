from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.backends import default_backend
import base64

class RSA:
    '''
    RSA (Rivest-Shamir-Adleman)
    A cryptographic class to perform RSA operations.
    '''
    
    @staticmethod
    def load_pem_private_key_from_file(path: str) -> rsa.RSAPrivateKey:
        try:
            with open(path, "rb") as file:
                private_key = load_pem_private_key(data = file.read(), 
                                                password=None, 
                                                backend=default_backend())
                return private_key
            
        except Exception as ex:
            raise Exception('Failed to load private key.')

    @staticmethod
    def load_pem_public_key_from_file(path: str) -> rsa.RSAPublicKey:
        try:
            with open(path, "rb") as file:
                public_key = load_pem_public_key(data = file.read(), 
                                                backend = default_backend())
                return public_key
            
        except Exception as ex:
            raise Exception('Failed to load public key.')

    @staticmethod
    def decrypt(priv_key: rsa.RSAPrivateKey, cipher_text: bytes, padding: padding) -> bytes:
        try:
            plain_data = priv_key.decrypt(
                ciphertext = cipher_text,
                padding = padding
            )
            return plain_data
        
        except Exception as ex:
            raise Exception('Failed to decrypt.')
    
    @staticmethod
    def encrypt(public_key: rsa.RSAPublicKey, plain_text: bytes, padding: padding) -> bytes:
        try:
            cipher_data = public_key.encrypt(
                plaintext = plain_text,
                padding = padding
            )
            return cipher_data
        
        except Exception as ex:
            raise Exception('Failed to encrypt.')
    