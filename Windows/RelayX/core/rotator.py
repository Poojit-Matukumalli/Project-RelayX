import asyncio, sys, os ; from time import time

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from Keys.public_key_private_key.generate_keys import handshake_initiator
from RelayX.utils.queue import rotation_lock, rotation_started
from RelayX.utils.config import ROTATE_INTERVAL
from RelayX.utils import config

last_rotate_time = time()

async def ensure_rotation_started():
    global rotation_started
    async with rotation_lock:
        if not rotation_started:
            rotation_started = True

async def key_rotation(user_onion, peer_onion, send_via_tor, handshake_initiator):
    return await handshake_initiator(user_onion, peer_onion, send_via_tor)

async def auto_rotation_monitor(user_onion, peer_onion, send_via_tor):
    """
    Background thread to automatically rotate keys every ROTATE_INTERVAL seconds.
    """
    global last_rotate_time, recipient_onion
    while True:
        try:
            if not recipient_onion:
                await asyncio.sleep(5)
                continue
            if time() - last_rotate_time >= ROTATE_INTERVAL:
                config.session_key[peer_onion] = await key_rotation(user_onion,peer_onion, send_via_tor, handshake_initiator)
                last_rotate_time = time()
            asyncio.sleep(30)
        except Exception as e:
            await asyncio.sleep(1)

