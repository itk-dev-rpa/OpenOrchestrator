"""Database access functions for constants and credentials.

Credential passwords are encrypted at rest with the key managed by
:mod:`OpenOrchestrator.common.crypto_util`.
"""

from sqlalchemy import select

from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database.constants import Constant, Credential
from OpenOrchestrator.database.db_util import _get_session
from OpenOrchestrator.database.exceptions import (
    ConstantNotFoundError,
    CredentialNotFoundError,
)


def get_constant(name: str) -> Constant:
    """Get a constant from the database.

    Args:
        name: The name of the constant.

    Returns:
        Constant: The constant with the given name.

    Raises:
        ConstantNotFoundError: If no constant with the given name exists.
    """
    with _get_session() as session:
        constant = session.get(Constant, name)
        if constant is None:
            raise ConstantNotFoundError(f"No constant with name '{name}' was found.")
        return constant


def get_constants() -> tuple[Constant, ...]:
    """Get all constants in the database."""
    with _get_session() as session:
        query = select(Constant).order_by(Constant.name)
        result = session.scalars(query).all()
        return tuple(result)


def create_constant(name: str, value: str) -> None:
    """Create a new constant in the database.

    Args:
        name: The name of the constant.
        value: The value of the constant.
    """
    with _get_session() as session:
        constant = Constant(name=name, value=value)
        session.add(constant)
        session.commit()


def update_constant(name: str, new_value: str) -> None:
    """Updates an existing constant with a new value.

    Args:
        name: The name of the constant to update.
        new_value: The new value of the constant.

    Raises:
        ConstantNotFoundError: If no constant with the given name exists.
    """
    with _get_session() as session:
        constant = session.get(Constant, name)

        if not constant:
            raise ConstantNotFoundError(f"No constant with name '{name}' was found.")

        constant.value = new_value
        session.commit()


def delete_constant(name: str) -> None:
    """Delete the constant with the given name from the database.

    Args:
        name: The name of the constant to delete.
    """
    with _get_session() as session:
        constant = session.get(Constant, name)
        session.delete(constant)
        session.commit()


def get_credential(name: str, decrypt_password: bool = True) -> Credential:
    """Get a credential from the database.
    The password of the credential is decrypted by default.

    Args:
        name: The name of the credential.
        decrypt_password: Whether to decrypt the credential password or not.

    Returns:
        Credential: The credential with the given name.

    Raises:
        CredentialNotFoundError: If no credential with the given name exists.
    """
    with _get_session() as session:
        credential = session.get(Credential, name)

    if credential is None:
        raise CredentialNotFoundError(f"No credential with name '{name}' was found.")

    if decrypt_password:
        credential.password = crypto_util.decrypt_string(credential.password)

    return credential


def get_credentials() -> tuple[Credential, ...]:
    """Get all credentials in the database (passwords stay encrypted)."""
    with _get_session() as session:
        query = select(Credential).order_by(Credential.name)
        result = session.scalars(query).all()
        return tuple(result)


def create_credential(name: str, username: str, password: str) -> None:
    """Create a new credential in the database.
    The password is encrypted before being persisted.

    Args:
        name: The name of the credential.
        username: The username of the credential.
        password: The password of the credential (plain text).
    """
    password = crypto_util.encrypt_string(password)

    with _get_session() as session:
        credential = Credential(
            name=name,
            username=username,
            password=password,
        )
        session.add(credential)
        session.commit()


def update_credential(name: str, new_username: str, new_password: str) -> None:
    """Updates an existing credential with a new username and password.

    Args:
        name: The name of the credential to update.
        new_username: The new username of the credential.
        new_password: The new password (plain text — will be encrypted).

    Raises:
        CredentialNotFoundError: If no credential with the given name exists.
    """
    new_password = crypto_util.encrypt_string(new_password)

    with _get_session() as session:
        credential = session.get(Credential, name)

        if not credential:
            raise CredentialNotFoundError(f"No credential with name '{name}' was found.")

        credential.username = new_username
        credential.password = new_password
        session.commit()


def delete_credential(name: str) -> None:
    """Delete the credential with the given name from the database.

    Args:
        name: The name of the credential to delete.
    """
    with _get_session() as session:
        credential = session.get(Credential, name)
        session.delete(credential)
        session.commit()
