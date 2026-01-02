from fastapi import APIRouter   ;   from plyer import notification
import asyncio, os

from RelayX.database.models import init_db
from RelayX.core.inbound import inbound_listener
from RelayX.core.tor_bootstrap import start_tor
from RelayX.utils.config import user_onion
from RelayX.database.crud import cleanup_tokens

router = APIRouter()

@router.post("/init")
async def init_backend():
    if not user_onion:
        notification.notify(title="RelayX Core: [Severe]", message=f"Unable to load your Networking Identity. Please restart the Network service", timeout=4)
        return {"Error" : "Networking Identity not found"}
    os.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..'))
    start_tor()
    asyncio.create_task(init_db())
    asyncio.create_task(cleanup_tokens())
    asyncio.create_task(inbound_listener())
    return {"Status" : "Initialized", "user_onion" : user_onion}