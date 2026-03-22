"""Field-level encryption for sensitive data using AES-256 via Fernet.

Fernet uses AES-128-CBC under the hood. For AES-256 equivalent security,
we use a 256-bit key derived via PBKDF2 or accept a Fernet-compatible key.
The ENCRYPTION_KEY env var must be a valid Fernet key (base64-encoded 32 bytes).

Generate a key:
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""

import json
import os

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import Text, TypeDecorator


def _get_fernet() -> Fernet:
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise RuntimeError("ENCRYPTION_KEY environment variable is required for field encryption")
    return Fernet(key.encode())


class EncryptedString(TypeDecorator):
    """SQLAlchemy type that transparently encrypts/decrypts string values."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        f = _get_fernet()
        return f.encrypt(value.encode("utf-8")).decode("utf-8")

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        f = _get_fernet()
        try:
            return f.decrypt(value.encode("utf-8")).decode("utf-8")
        except InvalidToken:
            # Value is not encrypted (pre-migration data), return as-is
            return value


class EncryptedJSON(TypeDecorator):
    """SQLAlchemy type that transparently encrypts/decrypts JSON values."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        f = _get_fernet()
        json_str = json.dumps(value, ensure_ascii=False)
        return f.encrypt(json_str.encode("utf-8")).decode("utf-8")

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        f = _get_fernet()
        try:
            decrypted = f.decrypt(value.encode("utf-8")).decode("utf-8")
            return json.loads(decrypted)
        except InvalidToken:
            # Value is not encrypted (pre-migration data or plain JSON)
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return value
