from fastapi import APIRouter, HTTPException
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)


from RelayX.models.request_models import ConnectModel
from RelayX.database.crud import fetch_chat_history, get_user, chat_history_load
from RelayX.utils.config import user_onion

router = APIRouter()

@router.post("/fetch_history")
async def fetch_history(payload: ConnectModel) -> dict:
    recipient_onion = payload.recipient_onion
    recipient_user = await get_user(recipient_onion)
    if not recipient_user:
        raise HTTPException(status_code=404, detail="User not found")
    chat_history = await chat_history_load(user_onion, recipient_onion)
    return {
        "onion_1" : user_onion,
        "onion_2" : recipient_onion,
        "chat_history" : chat_history
    }