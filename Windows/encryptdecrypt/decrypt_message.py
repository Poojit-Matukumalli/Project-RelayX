from cryptography.fernet import Fernet
import base64, os,sys
import hashlib

# =============================== Dynamic imports ======================================================================

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
    
from encryptdecrypt.shield_crypto import shield_decrypt, derive_shield_key

# =================================== Functions =======================================================================

def pad_key(key: bytes) -> bytes:
    key_hash = hashlib.sha256(key).digest()
    return base64.urlsafe_b64encode(key_hash)

# -------------------------------------------------------------

def decrypt_message(chat_key: bytes, ciphertext: str) -> str:
    try:
        # Step 1: Fernet decryption
        fernet_key = pad_key(chat_key)
        fernet = Fernet(fernet_key)
        decrypted = fernet.decrypt(ciphertext.encode()).decode()

        # Step 2: Use same derived shield key and decrypt
        shield_key = derive_shield_key(chat_key)
        unwrapped = shield_decrypt(shield_key, decrypted)

        return unwrapped
    except Exception as e:
        print(f"[DECRYPT ERROR] {e}")
        return ""
    