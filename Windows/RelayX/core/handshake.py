import os, sys

WINDOWS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if WINDOWS_DIR not in sys.path:
    sys.path.insert(0, WINDOWS_DIR)

from Keys.public_key_private_key.generate_keys import handshake_initiator

async def do_handshake(user_onion, recipient_onion, send_via_tor):
    return await handshake_initiator(user_onion, recipient_onion, send_via_tor)