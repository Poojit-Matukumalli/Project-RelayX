from fastapi import APIRouter, HTTPException
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)


from RelayX.models.request_models import ConnectModel
from RelayX.database.crud import fetch_chat_history, get_user
from RelayX.utils.config import user_onion

router = APIRouter()

@router.post("/fetch_history")
async def fetch_history(payload: ConnectModel):
    global user_onion
    recipient = payload.recipient_onion
    recipient_user = await get_user(recipient)
    if not recipient_user:
        raise HTTPException(status_code=404, detail="User not found")
    chat_history = await fetch_chat_history(user_onion, recipient)
    return {"chat_history": chat_history}
