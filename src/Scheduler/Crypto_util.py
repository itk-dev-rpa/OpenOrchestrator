from cryptography.fernet import Fernet

_enryption_key = None

def set_key(key:str):
    global _enryption_key 
    _enryption_key = key

def get_key():
    return _enryption_key

def validate_key(key:str):
    try:
        Fernet(key)
        return True
    except:
        return False