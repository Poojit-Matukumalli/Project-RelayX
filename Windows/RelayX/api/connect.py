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
from RelayX.utils import config
router = APIRouter()

@router.post("/connect")
async def connect(model : ConnectModel) -> dict:
    global recipient_onion, user_onion
    recipient_onion = model.recipient_onion
    ok = await verify_connection(recipient_onion)
    if not ok:
        return {"status" : "Offline"}
    config.session_key[recipient_onion] = await do_handshake(user_onion, recipient_onion, send_via_tor)
    if not config.session_key[recipient_onion]:
        return {"status" : "Handshake failed"}
    await ensure_rotation_started()
    return {
        "status" : "Connected"}
