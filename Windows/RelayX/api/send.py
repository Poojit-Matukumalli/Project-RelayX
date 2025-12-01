from fastapi import APIRouter  ;  import sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from utilities.encryptdecrypt.encrypt_message import encrypt_message
from utilities.network.Client_RelayX import relay_send, send_via_tor
from RelayX.models.request_models import SendModel, ConnectModel
from RelayX.utils.config import ROTATE_AFTER_MESSAGES, user_onion
from RelayX.core.rotator import key_rotation
from Keys.public_key_private_key.generate_keys import handshake_initiator
from RelayX.database.crud import add_message
from RelayX.utils.keyring_manager import keyring_load_key
from RelayX.utils import config
import uuid

router = APIRouter()
db_key = keyring_load_key()

@router.post("/send")
async def send_message(model : SendModel, connect : ConnectModel):
    global user_onion
    recipient_onion = connect.recipient_onion
    config.session_key[recipient_onion] = await handshake_initiator(user_onion, recipient_onion, send_via_tor)
    plaintext = model.msg
    recipient = connect.recipient_onion
    encrypted_for_db = encrypt_message(db_key, plaintext)
    await add_message(user_onion, recipient, encrypted_for_db, str(uuid.uuid4()))
    cipher = encrypt_message(config.session_key[recipient_onion],plaintext)

    await relay_send(cipher, user_onion, model.recipient_onion, show_route=False)
    config.message_count += 1
    if config.message_count >= ROTATE_AFTER_MESSAGES:
        config.session_key[recipient_onion] = await key_rotation(model.recipient_onion, send_via_tor, handshake_initiator)
        config.message_count = 0
    return {"ok" : True}
