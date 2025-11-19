"""                     Executor.py

This is the main script that handles the chat loop, Function calls and future UI connections.
It accesses functions which are all across several files.
A part of Project RelayX, by Poojit Matukumalli
Suggestions and improvements are Welcome (Not AI btw)
"""
# ============================ Imports ================================================================================
import json, subprocess, sys            
import asyncio, os, signal

# ============= Dynamic imports ========================================================================================

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from Keys.public_key_private_key.generate_keys import handshake_initiator
from Initial_Node import start_client, verify_connection
from Client_RelayX import send_via_tor, inbound_listener, handle_handshake_key


# ==================== USERNAME & PASSWORD ==============================================================================

filename = r"Windows\network\details.json" # Temporary file. will be replaced 
with open(filename, "r") as f:
    data = json.load(f)
    username = data["Username"]
    password = data["Password"]

# =================== Onion setup ======================================================================================

addr_file = os.path.join("Windows", "network", "Networking", "data", "HiddenService","hostname")
network_service = os.path.join("Windows", "network", "network_service.py")

if not os.path.exists(addr_file):
    subprocess.Popen([f"python -u {network_service}"],
            creationflags= subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL         
    )
if os.path.exists(addr_file):
    with open(addr_file, "r") as f:
        addr_user_onion = f.read()
else:
    print("[ERROR] Unable to fetch onion")

# ================ Background tor process ==============================================================================

tor_path = os.path.join("Windows","network", "Networking", "tor", "tor.exe")
Tor_bg_process = subprocess.Popen([
        tor_path],
        creationflags= subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
        stdout=subprocess.DEVNULL,
        stderr= subprocess.DEVNULL
)

# ==================== Configuration ===================================================================================
session_key = None
user_onion = addr_user_onion    # TODO : Add actual data fetcher using SQLite or something else
recipient_onion = ""            # TODO : add it so that the message page, on which the user is on decides it. Hopefully... after the UI 
relay_file = os.path.join("Windows", "network", "relay_list.json")
proxy = ("127.0.0.1", 9050)
listen_port = 5050

# ==================== Helpers =========================================================================================
async def inbound_listener_func():
    global session_key
    async def _handler(reader, writer):
        if session_key is None:
            session_key = await handle_handshake_key(reader, writer)
        else:
            await inbound_listener()
    server = await asyncio.start_server(_handler, '127.0.0.1', listen_port)
    async with server:
        await server.serve_forever()

async def listener_task():
    await inbound_listener_func()
    
# ==================================== Main loop ======================================================================= 

async def main():
    global session_key
    print("-" * 120)
    print(f"{" "*50}Project RelayX\n")
    global username, password
    print(f"Your Onion ID: {user_onion}")
    global recipient_onion
    recipient_onion = input("Enter peer's Onion address: ").strip()

    
    online = await verify_connection(recipient_onion)
    if online:
        asyncio.create_task(listener_task())
        session_key = await handshake_initiator(user_onion, recipient_onion, send_via_tor)
        print(session_key)
        if session_key:
            await start_client(user_onion, recipient_onion, session_key)
        else:
            print("Handshake Failed")
    else:
        print("Offline")

# ==================================== Running & Error handling ========================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Relay Shutting down.")
        try:
            Tor_bg_process.send_signal(signal.SIGINT)
            Tor_bg_process.wait(timeout=10)
        except Exception:
            Tor_bg_process.terminate()
    except Exception as e:
        print(f"[ERR] {e}")
        pass