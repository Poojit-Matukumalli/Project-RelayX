import os, sys
import base64
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Constants
AESGCM_KEY_SIZE = 32          # 256-bit AES-GCM
AESGCM_NONCE_SIZE = 12        # recommended nonce size for GCM
HKDF_INFO = b"RelayX-shield-v1"  # context string for domain separation

def derive_shield_key(chat_key: bytes, salt: Optional[bytes] = None) -> bytes:
    # TODO, Add salt (optional) to HKDF for session uniqueness
    ikm = chat_key  # input key material
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=AESGCM_KEY_SIZE,
        salt=salt,
        info=HKDF_INFO,
    )
    return hkdf.derive(ikm)

# DO NOT CHANGE ASSOCIATED DATA UNLESS ALL YOUR CONTACTS DO THE SAME.
# CHANGING IT WILL CAUSE DECRYPTION KILLING ITSELF LIKE MY SANITY.

def shield_encrypt(key: bytes, plaintext: str, associated_data: Optional[bytes] = b"RelayX") -> str: 
    # Encrypts the plaintext using AES-GCM and returns urlsafe-base64 str
    try:
        aesgcm = AESGCM(key)
        nonce = os.urandom(AESGCM_NONCE_SIZE)
        ad_bytes = associated_data
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), associated_data=ad_bytes)
        payload = nonce + ciphertext
        return base64.urlsafe_b64encode(payload).decode()
    except Exception as e:
        # Keep error message vague as hell so logs don't leak secrets
        print(f"[SHIELD ENCRYPT ERROR]")
        return ""


def shield_decrypt(key: bytes, encoded: str, associated_data: Optional[bytes] = b"RelayX") -> str: 
    # Decrypts the urlsafe-base64 (nonce || ciphertext). On failure, this thing returns empty string.
    try:
        payload = base64.urlsafe_b64decode(encoded)
        if len(payload) < AESGCM_NONCE_SIZE + 16:  # 16 is minimum tag size
            raise ValueError("payload too short")
        nonce = payload[:AESGCM_NONCE_SIZE]
        ciphertext = payload[AESGCM_NONCE_SIZE:]
        aesgcm = AESGCM(key)
        ad_bytes = associated_data
        plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=ad_bytes)
        return plaintext.decode()
    except Exception as e:
        print(f"[SHIELD DECRYPT ERROR]")
        return ""