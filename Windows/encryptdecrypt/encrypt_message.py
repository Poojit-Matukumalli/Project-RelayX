from cryptography.fernet import Fernet
import base64
import hashlib
from encryptdecrypt.shield_crypto import shield_encrypt, derive_shield_key


def pad_key(key: str) -> bytes:
    key_hash = hashlib.sha256(key.encode()).digest()
    return base64.urlsafe_b64encode(key_hash)


def encrypt_message(chat_key: str, message: str) -> str:
    try:
        shield_key = derive_shield_key(chat_key)
        shielded = shield_encrypt(shield_key, message)
        if not shielded:
            raise RuntimeError("Shield encryption failed")
        fernet_key = pad_key(chat_key)
        fernet = Fernet(fernet_key)
        encrypted = fernet.encrypt(shielded.encode())

        return encrypted.decode()
    except Exception as e:
        print(f"[ENCRYPT ERROR] {e}")
        return ""