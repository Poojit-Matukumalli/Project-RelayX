import asyncio, json, sys, os, uuid, time, base64

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from RelayX.utils.queue import incoming_queue, ack_queue, rotation_lock
from utilities.encryptdecrypt.decrypt_message import decrypt_message, decrypt_bytes
from RelayX.utils.config import LISTEN_PORT, PROXY, user_onion
from utilities.network.Client_RelayX import send_via_tor
from RelayX.database.crud import add_message, get_username
from Keys.public_key_private_key.generate_keys import handshake_responder, handshake_initiator, make_init_message
from RelayX.utils import config
from RelayX.utils.queue import state_queue, pending_lock

listen_port = LISTEN_PORT
Ack_timeout = 3
Max_retries = 5
session_key = config.session_key


def force_json(object):
    if isinstance(object, dict):
        return object
    if isinstance(object, str):
        try:
            parsed = json.loads(object)
            if isinstance(parsed, dict):
                return parsed
        except Exception as e:
            print(f"\n[JSON PARSE ERROR]\n{e}")
            return {"raw" : object}
    return {"raw" : object}

async def handle_file_init(packet):
        msg_id = packet.get("msg_id")
        async with pending_lock:
            config.incoming_transfers[msg_id] = {
                "from" : packet["from"],
                "file_name" : packet["filename"],
                "total_chunks" : packet["total_chunks"],
                "received" : {},
                "ts" : time.time()
            }

async def handle_file_chunk(packet : dict):
    msg_id = packet.get("msg_id")
    idx = packet.get("chunk_index")
    async with pending_lock:
        transfer = config.incoming_transfers.get(packet["msg_id"])
        recipient_onion = packet["from"]
        if not transfer:
            return
    
        idx = packet["chunk_index"]
        if idx in transfer["received"]:
            return
    
    key = session_key.get(recipient_onion)

    raw = base64.b64decode(packet["data"])
    decrypted = decrypt_bytes(key, raw)
    transfer["received"][idx] = decrypted

    ack_env = {
                "type" : "FILE_ACK",
                "msg_id": msg_id,
                "chunk_index" : idx,
                "from": user_onion,
                "to": recipient_onion,
            }
    asyncio.create_task(send_via_tor(recipient_onion,5050, ack_env, PROXY))
    if len(transfer["received"]) == transfer["total_chunks"]:
        #Reassemble logic not done yet. Remove return then
        return


async def handle_file_chunk_ack(packet):
    msg_id = packet.get("msg_id")
    idx = packet["chunk_index"]
    async with pending_lock:
        transfer = config.pending_transfers[msg_id]
        if not transfer:
            return
        config.pending_transfers[msg_id]["chunks"].pop(idx, None)

        if not config.pending_transfers[msg_id]["chunks"]:
            del config.pending_transfers[msg_id]


async def handle_incoming(reader, writer):
    global user_onion, PROXY, session_key
    try:
        data = await asyncio.wait_for(reader.readline(), timeout=5.0)
        while data in [b'', b'\n']:
            await asyncio.sleep(0.05)
            data = await asyncio.wait_for(reader.readline(), timeout=5.0)
        if not data:
            print("READ EMPTY") ; return
        msg_raw = data.decode().strip()
        try:
            envelope = force_json(msg_raw)
            if not envelope:
                print("[NO ENVELOPE]")
            if not isinstance(envelope, dict):
                raise ValueError("JSON type is NOT dict")
            recipient_onion = str(envelope.get("from")).strip().replace("\n", "")

            envelope_type = envelope.get("type")

            if envelope_type in ["HANDSHAKE_INIT", "HANDSHAKE_RESP"]:
                await handshake_responder(envelope, user_onion, send_via_tor)
                print(f"[HANDSHAKE]\nSent To  {await get_username(recipient_onion )}")
                return
            
            elif envelope_type == "FILE_TRANSFER_INIT":
                await handle_file_init(envelope)
                return
            
            elif envelope_type == "FILE_ACK":
                await handle_file_chunk_ack(envelope)
                return
            
            elif envelope_type == "FILE_CHUNK":
                await handle_file_chunk(envelope)
                return

            elif envelope.get("is_ack"):
                await ack_queue.put(envelope)
                await state_queue.put(f"\n[ACK RECEIVED]\nMessage ID : {envelope.get('msg_id')}\n")
                return
            elif envelope.get("type") == "msg":
                recipient_username = await get_username(recipient_onion)
                msg_id = envelope.get("msg_id")
                msg = envelope.get("payload", "")
                decrypted = None

                if not session_key.get(recipient_onion):
                    print(f"[WARN] No session key for {recipient_onion}. cannoyt decrypt.\n[HANDSHAKE]\nInitiating with {recipient_username}")
                    async with rotation_lock:
                        if not session_key.get(recipient_onion): 
                            new_key = await handshake_initiator(user_onion, recipient_onion, send_via_tor, make_init_message)

                            if new_key:
                                session_key[recipient_onion] = new_key
                        while session_key.get(recipient_onion) is None:
                            await asyncio.sleep(0.05)

                    pass

                decrypted = decrypt_message(config.session_key.get(recipient_onion), msg)
                await incoming_queue.put(msg_id)
                await add_message(user_onion, recipient_onion, decrypted, msg_id)
                if decrypted:     
                    print(f"\n[INCOMING MESSAGE]\nFrom: {recipient_username}\nMsg: {decrypted}\n")
                    ack_env = {
                        "msg_id": envelope.get("msg_id"),
                        "from": user_onion,
                        "to": envelope.get("from"),
                        "stap": envelope.get("stap"),
                        "is_ack": True,
                    }
                    asyncio.create_task(send_via_tor(recipient_onion,5050, ack_env, PROXY))
            else:
                pass
        except Exception as e:
            print("[JSON/PARSING ERROR]", e)

    except Exception as e:
            print({"msg": f"[INBOUND ERROR] {e}"})

    finally:
        writer.close()
        await writer.wait_closed()

async def inbound_listener():
    global listen_port
    server = await asyncio.start_server(handle_incoming, "127.0.0.1", listen_port)
    print(f"[LISTENER] Active on 127.0.0.1:{listen_port}")
    async with server:
        await server.serve_forever()