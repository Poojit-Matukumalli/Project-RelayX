from fastapi import APIRouter
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)


from RelayX.database.crud import async_session
from RelayX.database.models import Message
from sqlalchemy import delete

router = APIRouter()

@router.post("/clear_chat")
async def clear_chat(user1, user2):
    """Both user1 and user2 must be onions"""
    async with async_session() as session:
        async with session.begin():
            await session.execute(delete(Message).where(
            ((Message.sender_onion == user1) & (Message.recipient_onion == user2)) | 
            ((Message.sender_onion == user2) & (Message.recipient_onion == user1)))) # type: ignore
    return {"status" : "Chat Cleared"}