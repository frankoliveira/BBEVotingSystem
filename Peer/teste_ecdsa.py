from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import ECDSA
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives import serialization

#CRIAÇÃO DE CHAVES
private_key = ec.generate_private_key(
    ec.SECP384R1()
)
public_key = private_key.public_key()

#ASSINATURA
data = b"this is some data I'd like to sign"

chosen_hash = hashes.SHA256()
hasher = hashes.Hash(chosen_hash)
hasher.update(data)
digest = hasher.finalize()
sig = private_key.sign(
    digest,
    ECDSA(utils.Prehashed(chosen_hash))
)

#VERIFICAÇÃO
public_key.verify(
    sig,
    digest,
    ECDSA(utils.Prehashed(chosen_hash))
)

#SERIALIZAÇÃO DA CHAVE PRIVADA
serialized_private = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

print(serialized_private)

#SERIALIZAÇÃO DA CHAVE PUBLICA
public_key = private_key.public_key()
serialized_public = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
print(serialized_public)


#CARREGAMENTO DA CHAVE PUBLICA
loaded_public_key = serialization.load_pem_public_key(
    serialized_public,
)

#CARREGAMENTO DA CHAVE PRIVADA
loaded_private_key = serialization.load_pem_private_key(
    serialized_private,
    password=None
)

loaded_public_key.verify(
    sig,
    digest,
    ECDSA(utils.Prehashed(chosen_hash))
)