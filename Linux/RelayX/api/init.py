from fastapi import APIRouter   ;   import sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from RelayX.database.models import init_db
from RelayX.core.inbound import inbound_listener
from RelayX.core.tor_bootstrap import start_tor
from RelayX.utils.config import user_onion
import asyncio, os

router = APIRouter()

@router.post("/init")
async def init_backend():
    if not user_onion:
            
            return {"Error" : "Networking Identity not found"}
    os.chdir(PROJECT_ROOT)
    start_tor()
    await init_db()
    asyncio.create_task(inbound_listener())
    return {"Status" : "Initialized", "user_onion" : user_onion}