import asyncio, json, sys, os, uuid

WINDOWS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if WINDOWS_DIR not in sys.path:
    sys.path.insert(0, WINDOWS_DIR)

from RelayX.utils.queue import incoming_queue, ack_queue
from rotator import session_key
from utilities.encryptdecrypt.decrypt_message import decrypt_message
from utils.config import LISTEN_PORT, PROXY
from utilities.network.Client_RelayX import send_via_tor
from onion_loader import load_onion

listen_port = LISTEN_PORT
Ack_timeout = 3
Max_retries = 5
user_onion = load_onion()

async def send_with_ack(recipient_onion, payload_env, timeout=3, retries = 3):
    global PROXY
    msg_id = str(uuid.uuid4())
    payload_env["msg_id"] = msg_id
    payload_env["is_ack"] = False

    for attempt in range(retries):
        ok = await send_via_tor(recipient_onion, 5050, payload_env,PROXY)
        if not ok:
            continue
        try:
            ack = await asyncio.wait_for(ack_queue.get(), timeout=timeout)
            if ack.get("msg_id") == msg_id:
                return True
        except asyncio.TimeoutError:
            return "Retrying.."
    return False

async def handle_incoming(reader, writer):
    global session_key, user_onion, PROXY
    try:
        data = await reader.read(8192)
        msg_raw = data.decode()

        try:
            envelope = json.loads(msg_raw)
            if envelope.get("is_ack"):
                await ack_queue.put(envelope)
                print(f"[ACK RECEIVED] msg_id={envelope.get('msg_id')}")
                return
            decrypted = decrypt_message(session_key, envelope.get("payload", ""))
            await incoming_queue.put({"msg": decrypted})

            print(f"\n[INCOMING MESSAGE]\nFrom: {envelope.get('from')}\nMsg: {decrypted}\n")
            ack_env = {
                "msg_id": envelope.get("msg_id"),
                "from": user_onion,
                "to": envelope.get("from"),
                "stap": envelope.get("stap"),
                "is_ack": True,
            }
            route = envelope.get("from")
            asyncio.create_task(send_with_ack(route, ack_env))

        except Exception as e:
            print("[JSON/PARSING ERROR]", e)
            await incoming_queue.put({"msg": msg_raw})

    except Exception as e:
        await incoming_queue.put({"msg": f"[INBOUND ERROR] {e}"})

    finally:
        writer.close()
        await writer.wait_closed()
async def inbound_listener():
    global listen_port
    server = await asyncio.start_server(handle_incoming, "127.0.0.1", listen_port)
    print(f"[LISTENER] Active on 127.0.0.1:{listen_port}")
    async with server:
        await server.serve_forever()
