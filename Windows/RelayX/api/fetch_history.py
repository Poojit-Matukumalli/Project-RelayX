from fastapi import APIRouter, HTTPException
from RelayX.models.request_models import ConnectModel
from RelayX.database.crud import fetch_chat_history, get_user
from RelayX.utils.config import username

router = APIRouter()

@router.post("/fetch_history")
async def fetch_history(payload: ConnectModel):
    global username
    recipient = payload.recipient
    sender_username = username
    recipient_user = await get_user(recipient)
    if not recipient_user:
        raise HTTPException(status_code=404, detail="User not found")
    chat_history = await fetch_chat_history(sender_username, recipient)
    return {"chat_history": chat_history}
