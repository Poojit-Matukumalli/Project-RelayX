import os, asyncio, sys

# --------------------------- Dynamic imports ----------------------------------------------------------------------------

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)
from RelayX.core.onion_loader import load_onion

#-------------------------------------- Configs --------------------------------------------------------------------------

ROTATE_INTERVAL = 600
ROTATE_AFTER_MESSAGES = 25
LISTEN_PORT = 5050
PROXY = ("127.0.0.1", 9050)
message_count = 0
session_key = {}

# Paths & onion -----------

tor_path = os.path.join(PROJECT_ROOT, "Networking", "tor", "tor.exe" )
details_json = os.path.join(PROJECT_ROOT, "utilities","network", "details.json")
relay_file = os.path.join(PROJECT_ROOT, "utilities", "network", "relay_list.json")

user_onion = asyncio.run(load_onion())
