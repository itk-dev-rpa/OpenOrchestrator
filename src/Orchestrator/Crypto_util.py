from cryptography.fernet import Fernet
import hashlib

_enryption_key = None

def generate_key():
    return Fernet.generate_key()

def set_key(key:str):
    global _enryption_key 
    _enryption_key = key

def encrypt_data(data: str):
    data = data.decode()

    # Add hash of data to use as checksum
    hash_data = sha256(data)
    data = hash_data + data
    
    return Fernet(_enryption_key).encrypt(data).decode()

def decrypt_data(data:str):
    data = data.encode()

    decrypted_data = Fernet(_enryption_key).decrypt(data)

    if len(decrypted_data) < 32:
        raise ValueError('Decrypted data is too short. The decryption key is not the same as the encryption key.')

    hash_data = decrypted_data[0:32]
    data = decrypted_data[32:]

    if hash_data == sha256(data):
        return data.decode()
    else:
        raise ValueError('Checksum not correct. The decryption key is not the same as the encryption key.')

def validate_key(key:str):
    try:
        Fernet(key)
        return True
    except:
        return False

def sha256(data:bytes):
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.digest()
