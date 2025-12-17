import asyncio, json, sys, os, struct, msgpack

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
from RelayX.core.file_transfer import handle_file_chunk, handle_file_chunk_ack, handle_file_init

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


async def read_framed_message(reader: asyncio.StreamReader):
    try:
        raw_len = await reader.readexactly(4)
        msg_len = struct.unpack("!I", raw_len)[0]

        payload = b""
        while len(payload) < msg_len:
            chunk = await reader.read(msg_len - len(payload))
            if not chunk:
                raise ConnectionError("Connection closed")
            payload += chunk
        return payload
    except Exception as e:
        raise e

async def handle_incoming(reader, writer):
    global user_onion, PROXY, session_key
    try:
        raw_len = await reader.readexactly(4)
        msg_len = struct.unpack("!I", raw_len)[0]
        payload = await reader.readexactly(msg_len)
        envelope = msgpack.unpackb(payload, raw=False)
        if not envelope:
            print("[NO ENVELOPE]")
        try:
            envelope_type = envelope.get("type")
            recipient_onion = str(envelope.get("from")).strip().replace("\n", "")

            if envelope_type in ["HANDSHAKE_INIT", "HANDSHAKE_RESP"]:
                await handshake_responder(envelope, user_onion, send_via_tor)
                username = await get_username(recipient_onion )
                if envelope_type == "HANDSHAKE_INIT":
                    print(f"[HANDSHAKE]\nSent To  {username}")
                else:
                    print(f"[HANDSHAKE] Received from {username}")
                return
            
            elif envelope_type == "FILE_TRANSFER_INIT":
                await handle_file_init(envelope)
                return
  
            elif envelope_type == "FILE_CHUNK":
                await handle_file_chunk(envelope)
                return

            elif envelope_type == "FILE_ACK":
                await handle_file_chunk_ack(envelope)
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
                        "type" : "ack_resp",
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
            pass

    finally:
        writer.close()
        await writer.wait_closed()

async def inbound_listener():
    global listen_port
    server = await asyncio.start_server(handle_incoming, "127.0.0.1", listen_port)
    print(f"[LISTENER] Active on 127.0.0.1:{listen_port}")
    async with server:
        await server.serve_forever()