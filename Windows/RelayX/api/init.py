from fastapi import APIRouter   ;   import sys, os

WINDOWS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if WINDOWS_DIR not in sys.path:
    sys.path.insert(0, WINDOWS_DIR)


from RelayX.core.inbound import inbound_listener
from RelayX.core.tor_bootstrap import start_tor
from RelayX.core.onion_loader import load_onion
import asyncio

router = APIRouter()

@router.post("/init")
async def init_backend():
    start_tor()
    user_onion = await load_onion()
    if not user_onion:
        return {"Error" : "Networking Identity not found"}
    asyncio.create_task(inbound_listener())
    return {"Status" : "Initialized"}