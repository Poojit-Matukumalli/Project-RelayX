from fastapi import APIRouter  ;  import sys, os

WINDOWS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if WINDOWS_DIR not in sys.path:
    sys.path.insert(0, WINDOWS_DIR)

from utilities.encryptdecrypt.encrypt_message import encrypt_message
from utilities.network.Client_RelayX import relay_send, send_via_tor
from RelayX.models.request_models import SendModel
from RelayX.utils.config import ROTATE_AFTER_MESSAGES
from RelayX.core.rotator import key_rotation
from Keys.public_key_private_key.generate_keys import handshake_initiator


router = APIRouter()

@router.post("/send")
async def send_message(model : SendModel):
    global session_key, user_onion, recipient_onion, message_count
    plaintext = model.msg
    cipher = encrypt_message(session_key ,plaintext)

    await relay_send(cipher, user_onion, recipient_onion, show_route=False)
    message_count += 1
    if message_count >= ROTATE_AFTER_MESSAGES:
        session_key = await key_rotation(recipient_onion, send_via_tor, handshake_initiator)
    return {"ok" : True}
