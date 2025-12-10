"""             Encrypter module

Encrypts messages. uses helpers from shield crypto module
Part of Project RelayX, By Poojit Matukumalli
"""

import os,sys

# =============================== Dynamic imports ======================================================================

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from utilities.encryptdecrypt.shield_crypto import shield_encrypt

# =================================== Functions =======================================================================

def encrypt_message(chat_key: bytes, message: str) -> str:
    try:
        encrypted = shield_encrypt(chat_key, message)
        if not encrypted:
            raise RuntimeError("[ENCRYPT ERROR] Encryption failed")
        return encrypted
    except Exception as e:
        return ""
