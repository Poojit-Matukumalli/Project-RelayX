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
PROXY = ("127.0.0.1", 5050)

# Paths & onion -----------
tor_path = os.path.abspath(os.path.join("Windows", "Networking", "tor", "tor.exe" ))
details_json = os.path.abspath(os.path.join("Windows", "utilities","network", "details.json"))
relay_file = os.path.abspath(os.path.join("Windows", "network", "relay_list.json"))

user_onion = asyncio.run(load_onion())
