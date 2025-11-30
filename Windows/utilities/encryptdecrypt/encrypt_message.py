"""             Encrypter module

Encrypts messages. uses helpers from shield crypto module
Part of Project RelayX, By Poojit Matukumalli
"""

from cryptography.fernet import Fernet
import base64, os, sys
import hashlib

# =============================== Dynamic imports ======================================================================

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from utilities.encryptdecrypt.shield_crypto import shield_encrypt, derive_shield_key

# =================================== Functions =======================================================================

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
