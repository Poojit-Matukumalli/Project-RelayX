from cryptography.fernet import Fernet
import base64, os, sys
import hashlib

# Fix import 
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from encryptdecrypt.shield_crypto import shield_encrypt, derive_shield_key


def pad_key(key: bytes) -> bytes:
    key_hash = hashlib.sha256(key).digest()
    return base64.urlsafe_b64encode(key_hash).decode()

def encrypt_message(chat_key: bytes, message: str) -> str:
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
