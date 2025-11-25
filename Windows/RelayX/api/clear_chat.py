from fastapi import APIRouter
from RelayX.database.crud import async_session
from RelayX.database.models import Message
from sqlalchemy import delete

router = APIRouter()

@router.post("/clear_chat")
async def clear_chat(user1, user2):
    async with async_session() as session:
        async with session.begin():
            await session.execute(delete(Message).where(
            ((Message.sender == user1) & (Message.recipient == user2)) | 
            ((Message.sender == user2) & (Message.recipient == user1))).order_by(Message.TIMESTAMP)) # type: ignore
    return {"status" : "Chat Cleared"}