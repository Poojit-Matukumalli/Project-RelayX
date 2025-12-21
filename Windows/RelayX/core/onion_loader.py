import asyncio, subprocess, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from utilities.network.network_service import tor_hostname_creation

async def load_onion():
    addr_file = os.path.join(PROJECT_ROOT, "Networking", "data", "HiddenService","hostname")
    if not os.path.exists(addr_file):
        await tor_hostname_creation()
    for _ in range(50):
        if os.path.exists(addr_file):
            with open(addr_file, "r") as f:
                user_onion = f.read().replace("\n", "").strip()
                return user_onion     
        await asyncio.sleep(0.2)
    return