from cryptography.fernet import Fernet
from cryptography.exceptions import InvalidSignature, InvalidKey

_enryption_key = None

def generate_key():
    return Fernet.generate_key()

def set_key(key:str):
    global _enryption_key 
    _enryption_key = key

def encrypt_string(data: str) -> str:
    data = data.encode()
    data = Fernet(_enryption_key).encrypt(data)
    return data.decode()

def decrypt_string(data:str) -> str:
    try:
        data = data.encode()
        data = Fernet(_enryption_key).decrypt(data)
        return data.decode()
    except InvalidSignature:
        raise ValueError("Couldn't verify signature. The decryption key is not the same as the encryption key.")

def validate_key(key:str):
    try:
        Fernet(key)
        return True
    except:
        return False

if __name__ == '__main__':
    import DB_util
    DB_util.connect('Driver={ODBC Driver 17 for SQL Server};Server=SRVSQLHOTEL03;Database=MKB-ITK-RPA;Trusted_Connection=yes;')
    set_key('9q6bRUn4pRY9kcEEnSrLwZTFn4-uCQUANUFuRESYf6w=')
    creds = DB_util.get_credentials()
    for c in creds:
        print(c)
        print(decrypt_string(c[2]))