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

WINDOWS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if WINDOWS_DIR not in sys.path:
    sys.path.insert(0, WINDOWS_DIR)

from RelayX.database.crud import add_user
from RelayX.utils.config import user_onion
# =================================== Configuration =======================================================================

details_json = os.path.join("Windows","utilities","network","details.json")
Service_Name = "RelayX"
key_name = "sign_key"
# -----------------------------------------------------------------------------------------------------------

def details_helper(parameter, mode):
    return json.load(open(os.path.join("Windows","utilities","network","details.json"), mode))[f"{parameter}"]

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
# ========================================== Email part ================================================================

def hash_encrypt(recipient_username, user=USERNAME, self_onion=user_onion):
    user_combo = [f"{user}", f"{recipient_username}"]
    bytes_m = b"".join(x.encode() for x in sorted(user_combo)) # bytes_m means bytes_material
    key = urlsafe_b64encode(sha256(bytes_m).digest())
    f = Fernet(key)
    encrypted = f.encrypt(self_onion.encode())
    return encrypted
 
# ------------------------------------------------------------------

def hash_decrypt(ciphertext, recipient_username, user=USERNAME):
    user_combo = [f"{user}", f"{recipient_username}"]
    bytes_m = b"".join(x.encode() for x in sorted(user_combo))
    key = base64.urlsafe_b64encode(sha256(bytes_m).digest())
    f = Fernet(key)
    decrypted = f.decrypt(ciphertext)
    return decrypted

# ------------------------------------------------------------------

def email_helper(user_email, password, recipient_email, subject, body):
    message = EmailMessage()
    message["From"] = user_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.set_content(body.decode() if isinstance(body, bytes) else body)

    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(user_email, password)
        s.send_message(message)

# -------------------------------------------------------------------------------------

def read_email(user_email=user_email, user_password=email_password, subject_filter=None):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user_email, user_password)
    mail.select("inbox")
    if subject_filter:
        search_criteria = f'(HEADER Subject "{subject_filter}")'
    else:
        search_criteria = "ALL"
    _, data = mail.search(None, search_criteria)
    email_ids = data[0].split()
    
    if not email_ids:
        return None
    
    latest_id = email_ids[-1]
    _, message_data = mail.fetch(latest_id, "(RFC822)")
    if not message_data:
        return None
    raw_email = None
    for part in message_data:
        if isinstance(part, tuple) and part[1]:
            raw_email = part[1]
            break
    if raw_email is None:
        return None
    if isinstance(raw_email, bytes):
        raw_str = raw_email.decode(errors="ignore")
    else:
        raw_str = str(raw_email)
    body = raw_str.split("\r\n\r\n", 1)[-1].strip()
    return body.encode()


# ------------------------------------------------------------------------------------------------------------

async def auto_add_user(recipient_username, recipient_email, user_email=user_email, password=email_password):
    global user_onion
    hash = hash_encrypt(recipient_username)
    msg_body = f"""
                {hash}
                {public_key_sign}
               """
    subject_line = f"RelayX invite"
    await asyncio.to_thread(email_helper, user_email, password, recipient_email, subject_line, msg_body)  


    async def helper_read():
        try:
            raw = await asyncio.to_thread(read_email, user_email, password, subject_filter="RelayX invite")
            if raw:
                recipient_onion = hash_decrypt(raw, recipient_username)
                recipient_public_key = None # temp
                await add_user(
                    username=recipient_username,
                    onion=recipient_onion.decode(),
                    email=recipient_email,
                )

        except Exception as e:
            await asyncio.sleep(2)
    await helper_read()

# -------------------------------------------

async def send_email(*args, **kwargs):
    await asyncio.to_thread(auto_add_user, *args, **kwargs)

async def email_read(*args,**kwargs):
    await asyncio.to_thread(read_email, *args,**kwargs)
    
