from phe import paillier, PaillierPrivateKey, PaillierPublicKey, EncryptedNumber
import json

class PheManager():
    @staticmethod
    def new_keys_512():
        '''
        Chave 512 bits.
        '''
        return paillier.generate_paillier_keypair(n_length=256)
    
    def generate_str_public_key(public_key: PaillierPublicKey) -> str:
        key = {
            "n": public_key.n
        }

        return json.dumps(key)
    
    def generate_str_private_key(private_key: PaillierPrivateKey) -> str:
        key = {
            "n": private_key.public_key.n,
            "p": private_key.p,
            "q": private_key.q
        }
        return json.dumps(key)
    
    def generate_str_encrypted_number(encrypted_number: EncryptedNumber):
        enc_number = {
            "ciphertext": encrypted_number.ciphertext,
            "exponent": encrypted_number.exponent
        }

        return json.dumps(enc_number)
    
    def load_public_key_from_str(public_key: str) -> PaillierPublicKey:
        key = json.loads(public_key)
        return PaillierPublicKey(n=int(key['n']))
    
    def load_private_key_from_str(private_key: str) -> PaillierPrivateKey:
        key = json.loads(private_key)
        public_key = PaillierPublicKey(n=int(key['n']))
        print('chave pri deu bom')
        return PaillierPrivateKey(public_key=public_key, p=int(key['p']), q=int(key['q']))