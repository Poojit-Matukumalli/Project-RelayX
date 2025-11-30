from fastapi import APIRouter
import os,sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from RelayX.models.request_models import ConnectModel
from utilities.network.Initial_Node import verify_connection
from utilities.network.Client_RelayX import send_via_tor
from RelayX.core.handshake import do_handshake
from RelayX.core.rotator import ensure_rotation_started
from RelayX.utils.config import user_onion
router = APIRouter()

recipient_onion = None
session_key = None

@router.post("/connect")
async def connect(model : ConnectModel):
    global recipient_onion, session_key, user_onion
    recipient_onion = model.recipient_onion
    ok = await verify_connection(recipient_onion)
    if not ok:
        return {"status" : "Offline"}
    session_key = await do_handshake(user_onion, recipient_onion, send_via_tor)
    if not session_key:
        return {"status" : "Handshake failed"}
    await ensure_rotation_started()
    return {
        "status" : "Connected"}
