import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return base64.b64encode(salt + key).decode()

def verify_password(stored: str, provided: str) -> bool:
    decoded = base64.b64decode(stored.encode())
    salt = decoded[:16]
    stored_key = decoded[16:]
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    try:
        kdf.verify(provided.encode(), stored_key)
        return True
    except Exception:
        return False