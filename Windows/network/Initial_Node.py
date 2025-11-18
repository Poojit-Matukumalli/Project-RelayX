"""
This Setup handles Online status verif and takes care of the message loop.
Basically, this thing is focused on client connections.

Author- Poojit Matukumalli
"""

from aiohttp_socks import open_connection
import sys, os, json, asyncio

# === PATH FIX (ensures proper imports) ===

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from network.Client_RelayX import relay_send, send_via_tor
from encryptdecrypt.shield_crypto import derive_shield_key
from encryptdecrypt.encrypt_message import encrypt_message
from Keys.public_key_private_key.generate_keys import make_init_message, make_resp_message

user_onion = os.path.join("Windows","network","Networking","data","HiddenService","hostname")
PEER_PUB_KEY = None
USERNAME = json.load(open(os.path.join("Windows","network","details.json"), "r"))["Username"]

async def start_client(user_onion, recipient_onion,session_key):
    print(f"[CLIENT READY] Type messages to send. '/exit' to quit.")
    shield_key = derive_shield_key(session_key)
    try:
        while True:
            msg = input("You: ")
            if msg.lower() == "/exit":
                break
            await relay_send(encrypt_message(session_key, msg), user_onion, recipient_onion)
    except Exception as e:
        print(f"[CLIENT ERROR] {e}")

# checks whether yo frnd online or not

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