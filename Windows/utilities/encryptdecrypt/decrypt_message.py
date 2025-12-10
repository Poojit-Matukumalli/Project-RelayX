from cryptography.fernet import Fernet
import base64, os,sys
import hashlib

# =============================== Dynamic imports ======================================================================

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from utilities.encryptdecrypt.shield_crypto import shield_decrypt, derive_shield_key

# =================================== Functions =======================================================================

def pad_key(key: bytes) -> bytes:
    key_hash = hashlib.sha256(key).digest()
    return base64.urlsafe_b64encode(key_hash).decode()

def decrypt_message(session_key: bytes, ciphertext: str) -> str:
    try:
        # Step 1: Fernet decryption
        fernet_key = pad_key(session_key)
        fernet = Fernet(fernet_key)
        decrypted = fernet.decrypt(ciphertext.encode()).decode()

        #Step 2: Shield decrypt
        unwrapped = shield_decrypt(session_key, decrypted)

        return unwrapped
    except Exception as e:
        print(f"[DECRYPT ERROR] {e}")
        return ""
    