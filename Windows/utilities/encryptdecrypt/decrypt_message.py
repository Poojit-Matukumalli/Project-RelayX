import os,sys

# =============================== Dynamic imports ======================================================================

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from utilities.encryptdecrypt.shield_crypto import shield_decrypt

# =================================== Functions =======================================================================

def decrypt_message(session_key: bytes, ciphertext: str) -> str:
    try:
        decrypted = shield_decrypt(session_key, ciphertext)
        return decrypted if decrypted else ""
    except Exception as e:
        print(f"[DECRYPT ERROR] Decryption failed")
        return ""
    