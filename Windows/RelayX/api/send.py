from fastapi import APIRouter  ;  import sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from utilities.encryptdecrypt.encrypt_message import encrypt_message
from utilities.network.Client_RelayX import relay_send, send_via_tor
from RelayX.models.request_models import SendModel, ConnectModel
from RelayX.utils.config import ROTATE_AFTER_MESSAGES
from RelayX.core.rotator import key_rotation
from Keys.public_key_private_key.generate_keys import handshake_initiator
from database.crud import add_message
from utils.keyring_manager import keyring_load_key

router = APIRouter()
db_key = keyring_load_key()

@router.post("/send")
async def send_message(model : SendModel, connect : ConnectModel):
    global session_key, user_onion, recipient_onion, message_count
    plaintext = model.msg
    recipient = connect.recipient_onion
    encrypted_for_db = encrypt_message(db_key, plaintext)
    await add_message(user_onion, recipient, encrypted_for_db)
    cipher = encrypt_message(session_key ,plaintext)

    await relay_send(cipher, user_onion, model.recipient_onion, show_route=False)
    message_count += 1
    if message_count >= ROTATE_AFTER_MESSAGES:
        session_key = await key_rotation(model.recipient_onion, send_via_tor, handshake_initiator)
    return {"ok" : True}
