from fastapi import APIRouter  ;  import sys, os

WINDOWS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if WINDOWS_DIR not in sys.path:
    sys.path.insert(0, WINDOWS_DIR)

from utilities.encryptdecrypt.encrypt_message import encrypt_message
from utilities.network.Client_RelayX import relay_send, send_via_tor
from RelayX.models.request_models import SendModel, ConnectModel
from RelayX.utils.config import ROTATE_AFTER_MESSAGES, username
from RelayX.core.rotator import key_rotation
from Keys.public_key_private_key.generate_keys import handshake_initiator
from database.crud import add_message
from utils.keyring_manager import keyring_load_key

router = APIRouter()
db_key = keyring_load_key()

@router.post("/send")
async def send_message(model : SendModel, connect : ConnectModel):
    global session_key, user_onion, recipient_onion, message_count, username
    plaintext = model.msg
    recipient = connect.recipient
    encrypted_for_db = encrypt_message(db_key, plaintext)
    await add_message(username, recipient, encrypted_for_db)
    cipher = encrypt_message(session_key ,plaintext)

    await relay_send(cipher, user_onion, model.recipient_onion, show_route=False)
    message_count += 1
    if message_count >= ROTATE_AFTER_MESSAGES:
        session_key = await key_rotation(model.recipient_onion, send_via_tor, handshake_initiator)
    return {"ok" : True}
