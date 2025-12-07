from cryptography.fernet import Fernet
import base64, os,sys
import hashlib

# =============================== Dynamic imports ======================================================================

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from utilities.encryptdecrypt.shield_crypto import shield_decrypt, derive_shield_key

# =================================== Functions =======================================================================

def decrypt_message(session_key: bytes, ciphertext: str) -> str:
    try:
        # Step 1: Fernet decryption
        fernet = Fernet(session_key)
        decrypted = fernet.decrypt(ciphertext.encode()).decode()

        # Step 2: Use same derived shield key and decrypt
        shield_key = derive_shield_key(session_key)
        unwrapped = shield_decrypt(shield_key, decrypted)

        return unwrapped
    except Exception as e:
        print(f"[DECRYPT ERROR] {e}")
        return ""
    