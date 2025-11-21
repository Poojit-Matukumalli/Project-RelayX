from fastapi import APIRouter
import os,sys

WINDOWS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if WINDOWS_DIR not in sys.path:
    sys.path.insert(0, WINDOWS_DIR)

from RelayX.models.request_models import ConnectModel
from utilities.network.Initial_Node import verify_connection
from utilities.network.Client_RelayX import send_via_tor
from RelayX.core.handshake import do_handshake
from RelayX.core.rotator import ensure_rotation_started  
from RelayX.core.onion_loader import load_onion

router = APIRouter()

recipient_onion = None
session_key = None
user_onion = None

@router.post("/connect")
async def connect(model : ConnectModel):
    global recipient_onion, session_key, user_onion
    user_onion = await load_onion()
    recipient_onion = model.recipient
    ok = await verify_connection(recipient_onion)
    if not ok:
        return {"status" : "Offline"}
    session_key = await do_handshake(user_onion, recipient_onion, send_via_tor)
    if not session_key:
        return {"status" : "Handshake failed"}
    await ensure_rotation_started()
    return {
        "status" : "Connected"}
