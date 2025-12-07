"""              Client_RelayX module

User side RelayX relay. Helpers for Recieving and sending messages.
By- Poojit Matukumalli
thats it. Go read the code 🙏
"""
# ==================== Imports =========================================================================================

import json, random, aiohttp_socks as asocks
import os, time, sys, uuid, asyncio
# ============================== Dynamic imports =======================================================================

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from utilities.encryptdecrypt.encrypt_message import encrypt_message
from utilities.encryptdecrypt.decrypt_message import decrypt_message
from Keys.public_key_private_key.generate_keys import handshake_responder
from RelayX.utils.config import user_onion, relay_file

# ========================= Helpers ====================================================================================
 
def load_active_relays():       # Loads active relays... Duh
    global relay_file
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

async def build_route(active_relays, min_hops=1, max_hops=1):
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
        writer.write((json.dumps(envelope) + "\n").encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        print(f"\n[OK] Envelope sent → {onion_route}:{port}\n")
    except Exception as e:
        print(f"\n[FAIL] Transmission error → {onion_route}:{port} | {e}")

# Helper, Accessed in the executor script --------------------------------------------------------------------------------

async def relay_send(message ,user_onion, recipient_onion,msg_uuid, show_route=True):
    try:
        active_relays = load_active_relays()
        if not active_relays:
            print("\n[ERR] No active relays found.")
            return

        route_relays = await build_route(active_relays, min_hops=1, max_hops=1)

        # route (user → relays → destination)
        route = [f"{user_onion}:5050"] + route_relays + [f"{recipient_onion}:5050"]
        if show_route:
            print("\n[ROUTE]\n")
            for i, hop in enumerate(route, start=1):
                print(f"Hop {i}. {hop.replace("\n", "")}")

        route.pop(0) # popping onion to avoid looping back

        envelope = {
            "route": route.copy(),
            "msg_id" : msg_uuid,
            "payload": message,
            "from": user_onion,
            "to": recipient_onion,
            "stap": time.time(),
            "type": "msg"
        }
        
        first_hop = route[0]
        host, port = parse_hostport(first_hop)
        if not host or port is None:
            print("\n[Error] Invalid first hop.\n")
            return
        proxy = ("127.0.0.1", 9050)
        await send_via_tor(host, port, envelope, proxy)

    except Exception as e:
        print(f"\n[ERR] Relay send failed: {e}\n")