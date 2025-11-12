import aiohttp_socks ; import subprocess
import time          ; import asyncio
import json
import hashlib
import sys, os

# === PATH FIX (ensures proper imports) ===

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# === IMPORTS ===
from encryptdecrypt.encrypt_message import encrypt_message
from encryptdecrypt.decrypt_message import decrypt_message
from Keys.chat_key.derive_chat_key import derive_chat_key
from Keys.chat_key.rotate_chat_key import rotate_chat_key, check_rotation, auto_rotation_monitor

from Client_RelayX import relay_send
# === GLOBAL CONFIG ===
HOST = "0.0.0.0"
PORT = 5050
BUFFER_SIZE = 4096

RelayX_Chat_Key = None
PEER_ADDR = None
PEER_PUB_KEY = None
USERNAME = None


# === NETWORK SETUP ===
async def handle_conn(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    global RelayX_Chat_Key
    addr = writer.get_extra_info("peername")
    print(f"[INCOMING CONNECT] {addr}")
    while True:
        try:
            data = await reader.read(BUFFER_SIZE)
            if not data:
                return

            msg = data.decode()

            # Handle key rotation sync
            if msg.startswith("KEYUPDATE:"):
                new_key = msg.split(":", 1)[1].strip()
                RelayX_Chat_Key = new_key
                print(f"\n[🔑 KEYUPDATE RECEIVED] Session key updated securely.")
                continue

            # Normal encrypted message
            if not isinstance(RelayX_Chat_Key, str):
                # If chat key is missing or it isn't a string, we cannot call decrypt_message
                print("\n[DECRYPT ERROR] No valid chat key available; cannot decrypt message.")
                continue

            decrypted = decrypt_message(RelayX_Chat_Key, msg)
            if decrypted:
                print(f"\nPeer: {decrypted}")
            else:
                print("\n[DECRYPT ERROR] Could not decrypt message.")

        except Exception as e:
            print(f"[CONNECTION ERROR] {e}")
        finally:
            writer.close()
            await writer.wait_closed()


async def start_listener(host = "0.0.0.0", port=5050):
    server = await asyncio.start_server(handle_conn, "127.0.0.1", port)
    async with server:
        await server.serve_forever()

    print("------------------------------------------")
    print(f"[LISTENING] on {HOST}:{PORT} ...")
    print("------------------------------------------")


async def start_client(user_onion, recipient_onion):
    print(f"[CLIENT READY] Type messages to send. 'exit' to quit.")

    try:
        while True:
            msg = input("You: ")
            if msg.lower() == "exit":
                break

            # Send message through the relay system
            await relay_send(
                message=msg,
                user_onion=user_onion,
                recipient_onion=recipient_onion
            )

    except Exception as e:
        print(f"[CLIENT ERROR] {e}")