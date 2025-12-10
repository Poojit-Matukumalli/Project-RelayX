from fastapi import APIRouter  ;  import sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from utilities.encryptdecrypt.encrypt_message import encrypt_message
from utilities.network.Client_RelayX import send_via_tor
from RelayX.models.request_models import SendModel
from RelayX.utils.config import ROTATE_AFTER_MESSAGES, user_onion
from RelayX.core.rotator import key_rotation
from RelayX.core.handshake import do_handshake
from RelayX.utils import config
from RelayX.core.send_msg import send_to_peer
import uuid

router = APIRouter()

@router.post("/send")
async def send_message(model : SendModel):
    global user_onion
    msg_id = str(uuid.uuid4())
    recipient_onion = model.recipient_onion
    if recipient_onion not in config.session_key:
        await do_handshake(user_onion, recipient_onion, send_via_tor)
    plaintext = model.msg
    cipher = encrypt_message(config.session_key[recipient_onion],plaintext)
    print(cipher)
    await send_to_peer(recipient_onion, user_onion, plaintext, cipher, msg_id)
    config.message_count += 1
    if config.message_count >= ROTATE_AFTER_MESSAGES:
        await do_handshake(user_onion, recipient_onion, send_via_tor)
        config.message_count = 0
    return {"ok" : True}
