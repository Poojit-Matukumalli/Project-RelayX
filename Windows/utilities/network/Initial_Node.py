"""
This Setup handles Online status verif and takes care of the message loop.
Basically, this thing is focused on client connections.

Author- Poojit Matukumalli
"""
# Imports
from aiohttp_socks import open_connection ; import sys, os, json, asyncio, smtplib
import imaplib, base64 ; from cryptography.fernet import Fernet
from hashlib import sha256  ; from base64 import urlsafe_b64encode
from cryptography.hazmat.primitives.asymmetric import ed25519 ; from cryptography.hazmat.primitives import serialization
# =============================== Dynamic imports ======================================================================

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


# =================================== Configuration =======================================================================

details_json = os.path.join("Windows","utilities","network","details.json")

hostname_path = os.path.join("Windows","Networking","data","HiddenService","hostname")
with open(hostname_path, "r") as f:
    user_onion = f.read()

# -----------------------------------------------------------------------------------------------------------

def details_helper(parameter, mode):
    return json.load(open(os.path.join("Windows","utilities","network","details.json"), mode))[f"{parameter}"]

def create_keys():
    private_key = ed25519.Ed25519PrivateKey.generate()  # None password is temp
    public_key = private_key.public_key()      

    with open("private_key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
            )
        )
    with open("public_key.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )
    return private_key, public_key

def load_priv_sign():
    with open(os.path.abspath("private_key.pem"), "rb") as f:
        public_key = serialization.load_pem_private_key(f.read(), password=None)
    return public_key

def load_pub_sign():
    with open(os.path.abspath("public_key.pem"), "rb") as f:
       private_key = serialization.load_pem_public_key(f.read())
       return private_key

# Details ------------------------------------------------------------------------------------------------------

if os.path.exists(os.path.abspath("private_key.pem")):
    private_key_sign = load_priv_sign()
    public_key_sign = load_pub_sign()
else:
    private_key_sign, public_key_sign = create_keys()

USERNAME = details_helper("Username", "r")
user_email = details_helper("Email", "r")
email_password = details_helper("Email_app_Password", "r")

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

def read_email(user_email=user_email, user_password=email_password):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user_email, user_password)
    mail.select("inbox")
    _, data = mail.search(None, "ALL")
    email_ids = data[0].split()
    
    if not email_ids:
        return None
    
    latest_id = email_ids[-1]
    _, message_data = mail.fetch(latest_id, "(RFC822)")
    raw_email = message_data[0][1]
    raw_str = raw_email.decode(errors="ignore")
    body = raw_str.split("\r\n\r\n", 1)[-1].strip()
    return body.encode()
    


async def auto_add_user(recipient_username, recipient_email, user_email=user_email, password=email_password):
    global user_onion
    msg = f"{hash_encrypt(recipient_username)}"
    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls() ; s.login(user_email, password)
        s.sendmail(user_email, recipient_email, msg)


    async def helper_read(recipient_username):
        raw = read_email()
        recipient_onion = hash_decrypt(raw, recipient_username)
        with open(os.path.join("Windows","network", "contacts.json"), "r+") as f:
            data = json.load(f)
            data[recipient_username] = recipient_onion.decode()
            f.seek(0)
            json.dump(data, f, indent=4)
    bg_process = asyncio.create_task(helper_read(recipient_username))
    await bg_process


print(private_key_sign)
print(public_key_sign)