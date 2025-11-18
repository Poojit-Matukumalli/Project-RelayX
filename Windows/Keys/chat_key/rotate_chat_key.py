import hashlib
import base64
import time
import threading
import sys, os

# Import fix
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from network.Client_RelayX import send_via_tor
from Keys.public_key_private_key.generate_keys import handshake_initiator

addr_file = os.path.join("Windows", "network", "Networking", "data", "HiddenService","hostname")
with open(addr_file, "r") as f:
    addr_user_onion = f.read()
user_onion = addr_user_onion
# Global state

MESSAGE_COUNTER = 0
LAST_ROTATE_TIME = time.time()

ROTATE_INTERVAL = 600           
ROTATE_AFTER_MESSAGES = 25


async def rotate_chat_key(peer_onion):
    global MESSAGE_COUNTER, LAST_ROTATE_TIME
    MESSAGE_COUNTER = 0
    LAST_ROTATE_TIME = time.time()

    print("\n------------------------------------------")
    print("[KEY ROTATION] New session key generated.")
    print(f"[ROTATED AT] {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("------------------------------------------\n")
    
    if peer_onion:
        try:
            session_key = await handshake_initiator(user_onion=user_onion, peer_onion=peer_onion, send_via_tor=send_via_tor)
        except Exception as e:
            print(f"[KEY ROTATION ERROR] Failed to perform handshake after rotation: {e}")
    return session_key


async def check_rotation(peer_onion):
    """
    Checks whether key rotation is needed (based on time or message count).
    """
    global MESSAGE_COUNTER, LAST_ROTATE_TIME

    now = time.time()
    MESSAGE_COUNTER += 1
    time_elapsed = now - LAST_ROTATE_TIME

    if MESSAGE_COUNTER >= ROTATE_AFTER_MESSAGES or time_elapsed >= ROTATE_INTERVAL:
        await rotate_chat_key(peer_onion)


def auto_rotation_monitor(peer_onion):
    """
    Background thread to automatically rotate keys every ROTATE_INTERVAL seconds.
    """
    async def monitor():
        global LAST_ROTATE_TIME
        while True:
            if time.time() - LAST_ROTATE_TIME >= ROTATE_INTERVAL:
                await check_rotation(peer_onion)
            time.sleep(30)  # check every 30 seconds

    threading.Thread(target=monitor, daemon=True).start()