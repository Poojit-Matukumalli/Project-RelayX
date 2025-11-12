"""
User side RelayX relay. Recieves and sends messages.
By- Poojit Matukumalli
thats it. Go read the code 🙏
"""
import json;      import random;
import asyncio;   import aiohttp_socks as asocks
import os;        import time  ; import subprocess
import signal


def load_active_relays():       # Loads active relays... Duh
    relay_file = os.path.join("RelayX","Project_RelayX", "network", "relay_list.json")
    try:
        with open(relay_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        relays = data.get("relays", [])
        active_relays = []
        for r in relays:
            if r.get("status") == "active" and r.get("onion"):
                addr = r["onion"]
                port = r.get("port", 5050)
                active_relays.append(f"{addr}:{port}")
        return active_relays
    except Exception as e:
        print(f"[ERR] Failed to load {relay_file}: {e}")
        return []

def encrypt_payload(msg: str) -> str:
    return f"ENCRYPTED::{msg}"              # TODO : Add Encryption

def decrypt_payload(msg: str) -> str:
    """Mock decryption — replace later."""
    if msg.startswith("ENCRYPTED::"):
        return msg[len("ENCRYPTED::"):]
    return msg

def parse_hostport(addr: str):
    try:
        h, p = addr.rsplit(":", 1)
        return h, int(p)
    except:
        return None, None

async def send_via_tor(onion_route: str, port: int, envelope: dict, proxy):
    try:
        reader, writer = await asocks.open_connection(
            proxy_host=proxy[0],
            proxy_port=proxy[1],
            host=onion_route,
            port=port
        )
        writer.write(json.dumps(envelope).encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        print(f"[OK] Envelope sent → {onion_route}:{port}")
    except Exception as e:
        print(f"[FAIL] Transmission error → {onion_route}:{port} | {e}")

# sending logic
async def relay_send(message,user_onion, recipient_onion, show_route=False):

    active_relays = load_active_relays()
    if not active_relays:
        print("[ERR] No active relays found.")
        return

    # this randomly chooses 2–4 relays
    route_relays = random.sample(active_relays, k=min(len(active_relays), random.randint(1,1)))

    # route (user → relays → destination)
    route = [user_onion] + route_relays + [recipient_onion]
    if show_route:
        print(f"[ROUTE] {' → '.join(route)}")

    envelope = {
        "route": route.copy(),
        "payload": encrypt_payload(message),
        "from": user_onion,
        "to": recipient_onion,
        "stap": time.time(),
        "meta": {"type": "msg"}
    }

    # Pop the user address to avoid looping
    route.pop(0)
    first_hop = route[0]
    host, port = parse_hostport(first_hop)
    if not host or port is None:
        print("[Error] Invalid first hop.")
        return
    proxy = ("127.0.0.1", 9050)
    await send_via_tor(host, port, envelope, proxy)

# the listener 
async def handle_incoming(reader, writer):
    try:
        data = await reader.read(8192)
        msg_raw = data.decode()
        try:
            envelope = json.loads(msg_raw)
            decrypted = decrypt_payload(envelope.get("payload", ""))
            print(f"\n[INCOMING MESSAGE]\nFrom: {envelope.get('from')}\nMsg: {decrypted}\n")
        except Exception:
            print(f"[RAW INCOMING DATA]: {msg_raw}")
    except Exception as e:
        print(f"[ERR] Inbound handler crashed: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def inbound_listener():
    listen_port = 5050
    server = await asyncio.start_server(handle_incoming, "127.0.0.1", listen_port)
    print(f"[LISTENER] Active on 127.0.0.1:{listen_port}")
    async with server:
        await server.serve_forever()

