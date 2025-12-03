from fastapi import APIRouter  ;  import sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from utilities.encryptdecrypt.encrypt_message import encrypt_message
from utilities.network.Client_RelayX import relay_send, send_via_tor
from RelayX.models.request_models import SendModel
from RelayX.utils.config import ROTATE_AFTER_MESSAGES, user_onion
from RelayX.core.rotator import key_rotation
from RelayX.core.handshake import do_handshake
from RelayX.database.crud import add_message
from RelayX.utils.keyring_manager import keyring_load_key
from RelayX.utils import config
import uuid

router = APIRouter()
db_key = keyring_load_key()

@router.post("/send")
async def send_message(model : SendModel):
    global user_onion
    recipient_onion = model.recipient_onion
    if recipient_onion not in config.session_key:
        await do_handshake(user_onion, recipient_onion, send_via_tor)
    plaintext = model.msg
    encrypted_for_db = encrypt_message(db_key, plaintext)
    await add_message(user_onion, recipient_onion, encrypted_for_db, str(uuid.uuid4()))
    cipher = encrypt_message(config.session_key[recipient_onion],plaintext)

    await relay_send(cipher, user_onion, recipient_onion, show_route=False)
    config.message_count += 1
    if config.message_count >= ROTATE_AFTER_MESSAGES:
        await do_handshake(user_onion, recipient_onion, send_via_tor)
        config.message_count = 0
    return {"ok" : True}
