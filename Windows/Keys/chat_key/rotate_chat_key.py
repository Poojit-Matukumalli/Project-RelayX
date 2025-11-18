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
from Keys.chat_key.derive_chat_key import derive_chat_key

addr_file = os.path.join("Windows", "network", "Networking", "data", "HiddenService","hostname")
with open(addr_file, "r") as f:
    addr_user_onion = f.read()
user_onion = addr_user_onion
# Global state
CHAT_KEY = None
MESSAGE_COUNTER = 0
LAST_ROTATE_TIME = time.time()

ROTATE_INTERVAL = 600           
ROTATE_AFTER_MESSAGES = 25


def rotate_chat_key(peer_onion):
    global CHAT_KEY, MESSAGE_COUNTER, LAST_ROTATE_TIME
    element = derive_chat_key()
    combo = f"{element}|{time.time()}"
    new_secret = hashlib.sha256(combo.encode()).digest()
    CHAT_KEY = base64.urlsafe_b64encode(new_secret).decode()

    MESSAGE_COUNTER = 0
    LAST_ROTATE_TIME = time.time()

    print("\n------------------------------------------")
    print("[KEY ROTATION] 🔄 New chat key generated.")
    print(f"[KEY HASH] {hashlib.sha256(CHAT_KEY.encode()).hexdigest()[:16]}...")
    print(f"[ROTATED AT] {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("------------------------------------------\n")
    
    if peer_onion:
        try:
            handshake_initiator(user_onion=user_onion, peer_onion=peer_onion, send_via_tor=send_via_tor)
        except Exception as e:
            print(f"[KEY ROTATION ERROR] Failed to perform handshake after rotation: {e}")

    return CHAT_KEY


def check_rotation(priv_key, peer_pub_key, peer_ip=None, peer_port=None):
    """
    Checks whether key rotation is needed (based on time or message count).
    """
    global MESSAGE_COUNTER, LAST_ROTATE_TIME

    now = time.time()
    MESSAGE_COUNTER += 1
    time_elapsed = now - LAST_ROTATE_TIME

    if MESSAGE_COUNTER >= ROTATE_AFTER_MESSAGES or time_elapsed >= ROTATE_INTERVAL:
        rotate_chat_key(priv_key, peer_pub_key, peer_ip, peer_port)


def auto_rotation_monitor(priv_key, peer_pub_key, peer_ip=None, peer_port=None):
    """
    Background thread to automatically rotate keys every ROTATE_INTERVAL seconds.
    """
    def monitor():
        global LAST_ROTATE_TIME
        while True:
            if time.time() - LAST_ROTATE_TIME >= ROTATE_INTERVAL:
                rotate_chat_key(priv_key, peer_pub_key, peer_ip, peer_port)
            time.sleep(30)  # check every 30 seconds

    threading.Thread(target=monitor, daemon=True).start()