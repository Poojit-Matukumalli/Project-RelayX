import os, asyncio, uuid, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from utilities.network.Client_RelayX import relay_send
from RelayX.utils import queue
from utilities.network.Initial_Node import verify_connection
from RelayX.database.crud import add_message

async def ack_relay_send(message, user_onion, recipient_onion):
    msg_id = str(uuid.uuid4())
    for Attempt in range(3):
        await relay_send(message=message, user_onion=user_onion, recipient_onion=recipient_onion,msg_uuid=msg_id, show_route=True)
        try:
            ack = await asyncio.wait_for(queue.ack_queue.get(), timeout=15)
            if ack["msg_id"] == msg_id:
                return True
        except asyncio.TimeoutError:
            continue
    return False

async def send_to_peer(recipient_onion, user_onion, plaintext,cipher, msg_id):
    online = await verify_connection(recipient_onion)
    if online:
        await ack_relay_send(cipher, user_onion, recipient_onion)
        await add_message(user_onion, recipient_onion, plaintext, msg_id)
    else:
        print("Peer offline")
