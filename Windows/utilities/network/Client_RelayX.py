"""              Client_RelayX module

User side RelayX relay. Helpers for Recieving and sending messages.
By- Poojit Matukumalli
thats it. Go read the code 🙏
"""
# ==================== Imports =========================================================================================

import json, random, aiohttp_socks as asocks
import os, time, sys, asyncio
# ============================== Dynamic imports =======================================================================

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from utilities.encryptdecrypt.encrypt_message import encrypt_message
from encryptdecrypt.decrypt_message import decrypt_message
from Keys.public_key_private_key.generate_keys import handshake_responder
from RelayX.core.onion_loader import load_onion
from RelayX.utils.config import user_onion

# ========================= Helpers ====================================================================================
 
def load_active_relays():       # Loads active relays... Duh
    relay_file = os.path.join("Windows","utilities", "network", "relay_list.json")
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

# Helpers ---------------------------------------------------------------------------------------------------------------

def encrypt_payload(chat_key: bytes, msg) -> str:
    return encrypt_message(chat_key, msg)              # TODO : GOTO encrypt_message

def decrypt_payload(chat_key: bytes, msg) -> str:
    return decrypt_message(chat_key, msg)              # TODO : GOTO decrypt_message
sys_rand = random.SystemRandom()

# Route builder (Helper)--------------------------------------------------------------------------------------------------

async def build_route(active_relays, min_hops=2, max_hops=2):
    if not active_relays:
        return []
    shuffled_list = active_relays.copy()
    sys_rand.shuffle(shuffled_list)

    k = min(len(shuffled_list), sys_rand.randint(min_hops, max_hops))
    route = shuffled_list[:k]
    return route

# Helper ----------------------------------------------------------------------------------------------------------------

def parse_hostport(addr: str):
    try:
        h, p = addr.rsplit(":", 1)
        return h, int(p)
    except:
        return None, None

# Helper, Accessed by relay_send() ---------------------------------------------------------------------------------------
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

# Helper, Accessed in the executor script --------------------------------------------------------------------------------

async def relay_send(message ,user_onion, recipient_onion, show_route=True):
    try:
        active_relays = load_active_relays()
        if not active_relays:
            print("[ERR] No active relays found.")
            return

        route_relays = await build_route(active_relays, min_hops=2, max_hops=2)

        # route (user → relays → destination)
        route = [user_onion] + route_relays + [recipient_onion]
        if show_route:
            print(f"[ROUTE] {' → '.join(route)}")

        envelope = {
            "route": route.copy(),
            "payload": message,
            "from": user_onion,
            "to": recipient_onion,
            "stap": time.time(),
            "type": "msg"
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

    except Exception as e:
        print(f"[ERR] Relay send failed: {e}")
            
# Helper. Listener & Incoming --------------------------------------------------------------------------------------------  

async def handle_handshake_key(reader, writer):
    try:
        data = await reader.read(8192)
        envelope = json.loads(data.decode())
        session_key = await handshake_responder(envelope, user_onion, send_via_tor)
        return session_key
    except Exception as e:
        print(f"[ERR] Handshake handler crashed: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

# ---------------------------------------------------
