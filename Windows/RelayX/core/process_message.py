import asyncio, msgpack, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from RelayX.utils.queue import incoming_queue, ack_queue
from utilities.encryptdecrypt.decrypt_message import decrypt_message
from RelayX.utils.config import PROXY, user_onion
from utilities.network.Client_RelayX import send_via_tor, send_via_tor_transport
from RelayX.database.crud import add_message, get_username, mark_delivered
from Keys.public_key_private_key.generate_keys import handshake_responder
from RelayX.core.handshake import do_handshake
from RelayX.utils import config
from RelayX.utils.queue import state_queue
from RelayX.core.file_transfer import handle_file_chunk, handle_file_chunk_ack, handle_file_init
from utilities.encryptdecrypt.shield_crypto import verify_AEAD_envelope

session_key = config.session_key
blocked_contacts = config.blocked_users 

async def handle_message(recipient_onion, envelope):
    recipient_username = await get_username(recipient_onion)
    msg_id = envelope.get("msg_id")
    msg = envelope.get("payload", "")
    decrypted = decrypt_message(config.session_key.get(recipient_onion), msg)
    await incoming_queue.put(msg_id)
    await add_message(user_onion, recipient_onion, decrypted, msg_id)
    if decrypted:     
        print(f"\n[INCOMING MESSAGE]\nFrom: {recipient_username}\nMsg: {decrypted}\n")
        ack_env = {
            "type" : "ack_resp",
            "msg_id": envelope.get("msg_id"),
            "to": recipient_onion,
            "stap": envelope.get("stap"),
            "is_ack": True,
        }
        asyncio.create_task(send_via_tor(recipient_onion,5050, ack_env, PROXY))
    else:
        print("[DECRYPT ERROR]\nDecryption was unsuccessful")


async def route_envelope(sender, envelope):
    envelope_type = envelope["type"]

    if envelope.get("is_ack"):
        msg_id = envelope.get('msg_id')
        await ack_queue.put(envelope)
        await state_queue.put(f"\n[ACK RECEIVED]\nMessage ID : {msg_id}\n")
        asyncio.create_task(mark_delivered(msg_id))
        return

    if envelope_type == "msg":
        await handle_message(sender, envelope)
    
    if envelope_type == "FILE_TRANSFER_INIT":
        await handle_file_init(envelope)
        return
    
    elif envelope_type == "FILE_CHUNK":
        await handle_file_chunk(envelope)
        return
    
    elif envelope_type == "FILE_ACK":
        await handle_file_chunk_ack(envelope)
        return

async def process_encrypted(recipient_onion, outer):
    key = session_key.get(recipient_onion)
    if not key:
        asyncio.create_task(do_handshake(user_onion, recipient_onion, send_via_tor_transport))
        return
    try:
        inner = verify_AEAD_envelope(outer["sealed_envelope"], key)
        envelope = msgpack.unpackb(inner, raw=False)
    except Exception as e:
        print("[AEAD DECRYPT ERROR]\nUnable to Decrypt AEAD envelope. Please restart the app\n", e)
        return
    asyncio.create_task(route_envelope(recipient_onion, envelope))


async def process_outer(outer : dict):
    sender = outer.get("from")
    if not isinstance(sender, str):
        print("string")
        return
    recipient_onion = sender.strip().replace("\n", "")
    if recipient_onion in blocked_contacts:
        return
    recipient_username = await get_username(recipient_onion)
    if outer.get("type") in ["HANDSHAKE_INIT", "HANDSHAKE_RESP"]:
        await handshake_responder(outer, user_onion, send_via_tor_transport)
        if outer.get("type") == "HANDSHAKE_INIT":
            print(f"[HANDSHAKE]\nSent To  {recipient_username}")
        else:
            print(f"[HANDSHAKE] Received from {recipient_username}")
        return
    asyncio.create_task(process_encrypted(recipient_onion, outer))