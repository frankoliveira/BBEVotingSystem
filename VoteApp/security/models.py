#DEMOSTRAÇÃO PAILLIER
from phe import paillier, PaillierPrivateKey, PaillierPublicKey, EncryptedNumber
    
phe_public_key, phe_private_key = paillier.generate_paillier_keypair(n_length=512)
print("public key - n: ", phe_public_key.n)
print("public key - g: ", phe_public_key.g)

sum_of_encrypted_votes = phe_public_key.encrypt(0)
print("EncrytedNumber ", sum_of_encrypted_votes.ciphertext())
print('EncryptedNumber exponent', sum_of_encrypted_votes.exponent)



for i in range(2):
    cipher_vote  = phe_public_key.encrypt(1)
    sum_of_encrypted_votes = sum_of_encrypted_votes + cipher_vote

print(f'encrypted sum of votes: {sum_of_encrypted_votes.ciphertext()}\n')

result = phe_private_key.decrypt(sum_of_encrypted_votes)
print(f'decrypted sum of votes: {result}')



enc_result = EncryptedNumber(public_key=phe_public_key,
                ciphertext=sum_of_encrypted_votes.ciphertext())

print('my decrypted sum of votes', phe_private_key.decrypt(enc_result))

