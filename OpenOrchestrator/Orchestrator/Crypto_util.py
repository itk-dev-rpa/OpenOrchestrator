from cryptography.fernet import Fernet
from cryptography.exceptions import InvalidSignature

_encryption_key = None

def generate_key():
    return Fernet.generate_key()

def set_key(key:str):
    global _encryption_key #pylint: disable=global-statement
    _encryption_key = key

def encrypt_string(data: str) -> str:
    data = data.encode()
    data = Fernet(_encryption_key).encrypt(data)
    return data.decode()

def decrypt_string(data:str) -> str:
    try:
        data = data.encode()
        data = Fernet(_encryption_key).decrypt(data)
        return data.decode()
    except InvalidSignature as exc:
        raise ValueError("Couldn't verify signature. The decryption key is not the same as the encryption key.") from exc

def validate_key(key:str):
    try:
        Fernet(key)
        return True
    except ValueError:
        return False