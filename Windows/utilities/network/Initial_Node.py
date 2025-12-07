"""
This Setup handles Online status verif and takes care of the message loop.
Basically, this thing is focused on client connections.

Author- Poojit Matukumalli
"""
# Imports
from email.message import EmailMessage
from aiohttp_socks import open_connection
import sys, os, json, asyncio, smtplib
import imaplib, base64
from cryptography.fernet import Fernet
from hashlib import sha256
from base64 import urlsafe_b64encode
from cryptography.hazmat.primitives.asymmetric import ed25519 ; from cryptography.hazmat.primitives import serialization
import keyring
# =============================== Dynamic imports ======================================================================

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)
from RelayX.database.crud import add_user
from RelayX.utils.config import user_onion
# =================================== Configuration =======================================================================

details_json = os.path.join(PROJECT_ROOT, "utilities", "network", "details.json")
Service_Name = "RelayX"
key_name = "sign_key"
# -----------------------------------------------------------------------------------------------------------

def details_helper(parameter, mode):
    return json.load(open(os.path.abspath(details_json), mode))[f"{parameter}"]

def create_priv_key():
    private_key = ed25519.Ed25519PrivateKey.generate()
    pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    keyring.set_password(Service_Name, key_name, pem.decode())
    return private_key

def load_priv_sign():
    global Service_Name, key_name
    stored_pem = keyring.get_password(Service_Name, key_name)
    if stored_pem:
        private_key = serialization.load_pem_private_key(stored_pem.encode(), password=None)
        return private_key
    else:
        return create_priv_key()

# Details ------------------------------------------------------------------------------------------------------

if os.path.exists(os.path.abspath("private_key.pem")):
    private_key_sign = load_priv_sign()
else:
    private_key_sign = create_priv_key()

USERNAME = details_helper("Username", "r")
user_email = details_helper("Email", "r")
email_password = details_helper("Email_app_Password", "r")
private_key_sign = load_priv_sign()
public_key_sign = private_key_sign.public_key()

# =================================== Functions =======================================================================

# checks recipient online status ---------------------------------------------------------------------------------

async def verify_connection(
        onion :str,
        port : int =5050,
        proxy=("127.0.0.1", 9050),
        timeout: float = 12.0
    ) -> bool:
    
    reader = writer = None
    try:
        co_routine = open_connection(
            proxy_host=proxy[0], proxy_port=proxy[1],
            host=onion, port=port
        )
        reader, writer = await asyncio.wait_for(co_routine, timeout=timeout)
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass
        return True
    except Exception:
        return False
    finally:
        if writer is not None:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass