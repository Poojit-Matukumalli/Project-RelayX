import hashlib, os

def derive_chat_key() -> str:
    random_bytes = os.urandom(32)
    fernet_key = hashlib.sha256(random_bytes).digest()

    return fernet_key