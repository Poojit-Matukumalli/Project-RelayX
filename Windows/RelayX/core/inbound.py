import asyncio, json, sys, os, uuid

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from RelayX.utils.queue import incoming_queue, ack_queue
from utilities.encryptdecrypt.decrypt_message import decrypt_message
from RelayX.utils.config import LISTEN_PORT, PROXY, user_onion
from utilities.network.Client_RelayX import send_via_tor, relay_send
from RelayX.database.crud import add_message, get_username
from RelayX.core.handshake import do_handshake
from RelayX.utils import config

listen_port = LISTEN_PORT
Ack_timeout = 3
Max_retries = 5

def force_json(object):
    while isinstance(object, str):
        try:
            object = json.loads(object)
        except Exception as e:
            print(f"\n[JSON PARSE ERROR]\n{e}") ; return
    return object

async def handle_incoming(reader, writer):
    global user_onion, PROXY
    try:
        data = await asyncio.wait_for(reader.readline(), timeout=5.0)
        while data == b'':
            await asyncio.sleep(0.05)
            data = await asyncio.wait_for(reader.readline(), timeout=5.0)
        if not data:
            print("READ EMPTY") ; return
        msg_raw = data.decode().strip()
        try:
            envelope = force_json(msg_raw)
            if not isinstance(envelope, dict):
                raise ValueError("JSON type is NOT dict")
            recipient_onion = str(envelope.get("from")).strip().replace("\n", "")

            if envelope.get("type") in ["HANDSHAKE_INIT", "HANDSHAKE_RESP"]:
                await do_handshake(user_onion, recipient_onion, send_via_tor)
                return 
            elif envelope.get("is_ack"):
                await ack_queue.put(envelope)
                print(f"\n[ACK RECEIVED]\nMessage ID : {envelope.get('msg_id')}\n")
                return
            else:
                recipient_username = await get_username(recipient_onion)
                msg_id = envelope.get("msg_id")
                msg = envelope.get("payload", "")
                #decrypted = decrypt_message(config.session_key[recipient_onion], envelope.get("payload", ""))
                #await add_message(user_onion, recipient_onion, decrypted, msg_id)
                print(f"\n[INCOMING MESSAGE]\nFrom: {recipient_username}\nMsg: {msg}\n")
                ack_env = {
                    "msg_id": envelope.get("msg_id"),
                    "from": user_onion,
                    "to": envelope.get("from"),
                    "stap": envelope.get("stap"),
                    "is_ack": True,
                }
                asyncio.create_task(send_via_tor(recipient_onion,5050,ack_env, PROXY))

        except Exception as e:
            print("[JSON/PARSING ERROR]", e)
            await incoming_queue.put({"msg": msg_raw})

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