from cryptography.fernet import Fernet

_enryption_key = None

def generate_key():
    return Fernet.generate_key()

def set_key(key:str):
    global _enryption_key 
    _enryption_key = key

def encrypt_data(data: str):
    return Fernet(_enryption_key).encrypt(data.encode()).decode()

def decrypt_data(data:str):
    return Fernet(_enryption_key).decrypt(data.encode()).decode()

def validate_key(key:str):
    try:
        Fernet(key)
        return True
    except:
        return False
