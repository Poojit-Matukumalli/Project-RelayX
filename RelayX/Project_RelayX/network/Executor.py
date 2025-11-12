import json;      import random;                
import asyncio;   import aiohttp_socks as asocks
import os;        import time  ; import subprocess
import signal;     import hashlib
import sys;       import threading

from Client_RelayX import inbound_listener, relay_send
from Initial_Node import start_client


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from Keys.chat_key.derive_chat_key import derive_chat_key
from Keys.chat_key.rotate_chat_key import auto_rotation_monitor


# Setting up the user's onion url/route/address or whatever it is
filename = r"RelayX\Project_RelayX\network\details.json"
with open(filename, "r") as f:
    data = json.load(f)
    username = data["Username"]
    password = data["Password"]

addr_file = os.path.join("RelayX","Project_RelayX","network", "Networking", "data", "HiddenService","hostname")
with open(addr_file, "r") as f:
    addr_user_onion = f.read()

# Setting up Tor in the background

tor_path = os.path.join("RelayX","Project_RelayX","network", "Networking", "tor", "tor.exe")
Tor_bg_process = subprocess.Popen([
        tor_path],
        creationflags= subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
        stdout=subprocess.DEVNULL,
        stderr= subprocess.DEVNULL
)


# Configuration ig
user_onion = addr_user_onion    # TODO : Add actual data fetcher using SQLite or something else
recipient_onion = ""
relay_file = os.path.join("RelayX","Project_RelayX", "network", "relay_list.json")
proxy = ("127.0.0.1", 9050)
listen_port = 5050

# running both
async def main():
    print("       Project RelayX\n")
    global username, password

    priv_key = hashlib.sha256((username + password).encode()).hexdigest()
    print(f"Your Onion ID: {user_onion}")
    global recipient_onion
    recipient_onion = input("Enter peer's Onion address: ").strip()

                                    #TODO:Derive initial chat key
    # Chat_Key = derive_chat_key(priv_key, "")
    # auto_rotation_monitor(priv_key, "")

    listener_thread = threading.Thread(target=lambda: inbound_listener, daemon=True)
    listener_thread.start()
    print("[LISTENING] Inbound listener started.")
    while True:
        try:
            msg = input("You: ").strip()
            if msg.lower() == "/exit":
                print("Exiting chat...")
                break
            await relay_send(msg, user_onion, recipient_onion)
        except Exception as e:
            print(f"[Loop error] {e}")

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
