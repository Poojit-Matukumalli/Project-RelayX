from fastapi import APIRouter  ;  import sys, os, asyncio

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from utilities.network.Client_RelayX import send_via_tor_transport
from RelayX.models.request_models import SendModel
from RelayX.utils.config import ROTATE_AFTER_MESSAGES, user_onion
from RelayX.core.handshake import do_handshake
from RelayX.utils import config
from RelayX.core.send_msg import send_to_peer
from RelayX.database.crud import add_message
import uuid

router = APIRouter()

@router.post("/send")
async def send_message(model : SendModel):
    global user_onion
    msg_id = str(uuid.uuid4())
    recipient_onion = model.recipient_onion
    if recipient_onion not in config.session_key:
        await do_handshake(user_onion, recipient_onion, send_via_tor_transport)
    plaintext = model.msg
    await send_to_peer(recipient_onion, user_onion, plaintext, msg_id)
    await add_message(user_onion, recipient_onion, plaintext, msg_id)
    config.message_count += 1
    if config.message_count >= ROTATE_AFTER_MESSAGES:
        await do_handshake(user_onion, recipient_onion, send_via_tor_transport)
        config.message_count = 0
    return {"ok" : True}