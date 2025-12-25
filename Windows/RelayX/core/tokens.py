import os, sys, asyncio, time, uuid, msgpack, secrets, traceback
from pathlib import Path

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(ROOT, '..', '..')
sys.path.insert(0, PROJECT_ROOT)

from RelayX.utils.config import user_onion, TOKEN_EXPIRY
from utilities.encryptdecrypt.token_crypto import encrypt_token_bytes, decrypt_token_bytes
from RelayX.database.crud import burn_token, add_token


def token_envelope(password : bytes):
    onion = encrypt_token_bytes(password, user_onion.encode())
    msg_id = str(uuid.uuid4())
    env = {
        "msg_id" : msg_id,
        "content" : onion,
        "ts" : int(time.time())
    }
    return msg_id, msgpack.packb(env, use_bin_type=True)


async def burn_after_delay(msg_id:str, delay):
    await asyncio.sleep(delay)
    await burn_token(msg_id)

def helper_GetTokenDir():
    base = Path.home() / "Documents" / ".cache"
    base.mkdir(parents=True, exist_ok=True)
    return base

async def create_token(password : str):
    base = helper_GetTokenDir()
    filename = secrets.token_hex(16) + ".dat"
    path = base / filename
    try:
        msg_id, token_bytes = token_envelope(password.encode())
        ciphertext = encrypt_token_bytes(password.encode(), token_bytes)
        with open(path, "w") as f:
            f.write(ciphertext)
            f.flush()
            os.fsync(f.fileno())
        await add_token(str(msg_id), str(path))
        asyncio.create_task(burn_after_delay(msg_id, 120))
        return str(Path(path))
    except Exception as e:
        return "Fail"
    
async def read_token(filepath, password):
    with open(filepath, "r") as f:
        ciphertext = f.read()
    try:
        decrypted = decrypt_token_bytes(ciphertext, password)
        cipher = msgpack.unpackb(decrypted, raw=False)
        print(cipher)
        onione = cipher.get("content")
        onion = decrypt_token_bytes(onione, password)
        print(onion)
    except Exception as e:
        pass