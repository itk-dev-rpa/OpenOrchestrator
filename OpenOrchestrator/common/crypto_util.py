"""This module handles cryptographic tasks in OpenOrchestrator."""

from cryptography.fernet import Fernet
from cryptography.exceptions import InvalidSignature


_ENCRYPTION_KEY: str | None = None


def generate_key() -> bytes:
    """Generates a new valid AES crypto key.

    Returns:
        bytes: A valid AES crypto key.
    """
    return Fernet.generate_key()


def set_key(key: str | None) -> None:
    """Set the crypto key for the module.
    The key will be used in all subsequent calls to this module.
    """
    global _ENCRYPTION_KEY  # pylint: disable=global-statement
    _ENCRYPTION_KEY = key


def get_key() -> str | None:
    """Get the encryption key last set using
    crypto_util.set_key.

    Returns:
        str: The encryption key, if any.
    """
    return _ENCRYPTION_KEY


def encrypt_string(data: str) -> str:
    """Encrypt a string using AES with the crypto key set using
    crypto_util.set_key.

    Args:
        data: The string to encrypt.

    Returns:
        str: The encrypted string.

    Raises:
        RuntimeError: If the encryption key has not been set.
    """
    if not _ENCRYPTION_KEY:
        raise RuntimeError("Can't encrypt without an encryption key.")

    byte_data = data.encode()
    byte_data = Fernet(_ENCRYPTION_KEY).encrypt(byte_data)
    return byte_data.decode()


def decrypt_string(data: str) -> str:
    """Decrypt a string using AES with the crypto key set using
    crypto_util.set_key.

    Args:
        data: The string to decrypt.

    Raises:
        ValueError: If the crypto key doesn't match the key that was used when encrypting.

    Returns:
        str: The decrypted string.

    Raises:
        RuntimeError: If the encryption key has not been set.
    """
    if not _ENCRYPTION_KEY:
        raise RuntimeError("Can't decrypt without an encryption key.")

    try:
        byte_data = data.encode()
        byte_data = Fernet(_ENCRYPTION_KEY).decrypt(byte_data)
    except InvalidSignature as exc:
        raise ValueError("Couldn't verify signature. The decryption key is not the same as the encryption key.") from exc

    return byte_data.decode()


def validate_key(key: str) -> bool:
    """Validate if a encryption key is a valid AES encryption key.

    Args:
        key: The key to validate.

    Returns:
        bool: True if the key is valid.
    """
    try:
        Fernet(key)
    except ValueError:
        return False

    return True
