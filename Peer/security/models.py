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

        with open(path + 'private_key.pem', 'wb') as file:
            file.write(pem_private_key)
            file.close()

    @staticmethod
    def save_pem_public_key(public_key: rsa.RSAPublicKey, path: str):
        pem_public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.PKCS1
        )

        with open(path + 'public_key.pem', 'wb') as file:
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
            raise Exception('Failed to load private key.')

    @staticmethod
    def load_pem_public_key_from_file(path: str) -> rsa.RSAPublicKey:
        try:
            with open(path, 'rb') as file:
                public_key = serialization.load_pem_public_key(
                    data = file.read(), 
                    backend = default_backend())
                return public_key
            
        except Exception as ex:
            raise Exception('Failed to load public key.')

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
        
"""
priv_key = rsa.generate_private_key(public_exponent=65537, key_size=1024)
CustomRSA.save_pem_private_key(private_key=priv_key, path='./')
CustomRSA.save_pem_public_key(public_key=priv_key.public_key(), path='./')

public_key = CustomRSA.load_pem_public_key_from_file('./public_key.pem')
private_key = CustomRSA.load_pem_private_key_from_file('./private_key.pem')

msg = 'Informacão secreta'
msg_encoded = msg.encode('utf-8')
enc_msg = CustomRSA.encrypt(public_key=public_key, plain_text=msg_encoded)
dec_msg = CustomRSA.decrypt(private_key=private_key, cipher_text=enc_msg)
print(f'mensagem descriptada: {dec_msg.decode('utf-8')}')

sign = CustomRSA.sign(private_key=private_key,
                      message=msg_encoded)

verification = CustomRSA.verify(public_key=public_key,
                                signature=sign,
                                message=msg_encoded)
print(f'verification: {verification}')
"""