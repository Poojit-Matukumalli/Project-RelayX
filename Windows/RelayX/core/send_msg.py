import os, asyncio, uuid, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from utilities.network.Client_RelayX import relay_send, send_via_tor_transport
from RelayX.utils import queue
from utilities.encryptdecrypt.encrypt_message import encrypt_message
from RelayX.utils import config
from RelayX.core.handshake import do_handshake

async def ack_relay_send(message, user_onion, recipient_onion):
    msg_id = str(uuid.uuid4())
    for Attempt in range(3):
        session_key = config.session_key.get(recipient_onion)
        if not session_key:
            await do_handshake(user_onion, recipient_onion, send_via_tor_transport)
        cipher = encrypt_message(session_key, message)
        await relay_send(message=cipher, user_onion=user_onion, recipient_onion=recipient_onion,msg_uuid=msg_id, show_route=True)
        try:
            ack = await asyncio.wait_for(queue.ack_queue.get(), timeout=15)
            if ack["msg_id"] == msg_id:
                return True
        except asyncio.TimeoutError:
            continue
    return False

async def send_to_peer(recipient_onion, user_onion, plaintext, msg_id):
    #online = await verify_connection(recipient_onion)
    online = True
    if online:
        await ack_relay_send(plaintext, user_onion, recipient_onion)
    else:
        print("Peer offline")