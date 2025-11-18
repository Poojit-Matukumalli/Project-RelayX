import json;      import random;                
import asyncio;   import aiohttp_socks as asocks
import os;        import time  ; import subprocess
import signal;     import hashlib
import sys;       import threading

from Initial_Node import start_client, verify_connection
from Client_RelayX import send_via_tor, inbound_listener, handle_handshake_key

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from Keys.public_key_private_key.generate_keys import handshake_initiator, handshake_responder
from Keys.chat_key.rotate_chat_key import auto_rotation_monitor


# Setting up the user's onion url/route/address or whatever it is
filename = r"Windows\network\details.json"  # TEMPORARY
with open(filename, "r") as f:
    data = json.load(f)
    username = data["Username"]
    password = data["Password"]

addr_file = os.path.join("Windows", "network", "Networking", "data", "HiddenService","hostname")
with open(addr_file, "r") as f:
    addr_user_onion = f.read()

# Setting up Tor in the background

tor_path = os.path.join("Windows","network", "Networking", "tor", "tor.exe")
Tor_bg_process = subprocess.Popen([
        tor_path],
        creationflags= subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
        stdout=subprocess.DEVNULL,
        stderr= subprocess.DEVNULL
)


# Configuration ig
session_key = None
user_onion = addr_user_onion    # TODO : Add actual data fetcher using SQLite or something else
recipient_onion = ""            # TODO : add it so that the message page, on which the user is on decides it. Hopefully... after the UI 
relay_file = os.path.join("Windows", "network", "relay_list.json")
proxy = ("127.0.0.1", 9050)
listen_port = 5050

# Helper
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

async def main():
    global session_key
    print("                                  Project RelayX\n")
    global username, password

    priv_key = hashlib.sha256((username + password).encode()).hexdigest()
    print(f"Your Onion ID: {user_onion}")
    global recipient_onion
    recipient_onion = input("Enter peer's Onion address: ").strip()

                                    #TODO:Derive initial chat key
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