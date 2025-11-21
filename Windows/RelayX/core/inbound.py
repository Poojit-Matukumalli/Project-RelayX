import asyncio, json, sys, os

WINDOWS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if WINDOWS_DIR not in sys.path:
    sys.path.insert(0, WINDOWS_DIR)

from RelayX.utils.queue import incoming_queue
from utilities.encryptdecrypt.decrypt_message import decrypt_message

async def handle_incoming(reader, writer):
    try:
        data = await reader.read(8192)
        msg_raw = data.decode()
        try:
            envelope = json.loads(msg_raw)          
            decrypted = decrypt_message(envelope.get("payload", ""))
            await incoming_queue.put({"msg": decrypted})
            print(f"\n[INCOMING MESSAGE]\nFrom: {envelope.get('from')}\nMsg: {decrypted}\n")
        except Exception:
            await incoming_queue.put({"msg" : msg_raw})
    except Exception as e:
        await incoming_queue.put({"msg" : f"[INBOUND ERROR] {e}"})
    finally:
        writer.close()
        await writer.wait_closed()

async def inbound_listener():
    global listen_port
    server = await asyncio.start_server(handle_incoming, "127.0.0.1", listen_port)
    print(f"[LISTENER] Active on 127.0.0.1:{listen_port}")
    async with server:
        await server.serve_forever()
