from sqlalchemy.future import select
from sqlalchemy import text
import os,sys

WINDOWS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if WINDOWS_DIR not in sys.path:
    sys.path.insert(0, WINDOWS_DIR)

from RelayX.database.db import async_session
from RelayX.database.models import User, Message
from utilities.encryptdecrypt.decrypt_message import decrypt_message
from utilities.encryptdecrypt.encrypt_message import encrypt_message
from RelayX.utils.keyring_manager import keyring_load_key

# Users ------------------------------------------------------------------------------------------------

key = keyring_load_key()

async def add_user(username : str, onion : str, email : str):
    async with async_session() as session:
        async with session.begin():
            user = User(username=username, onion=onion, email=email)
            session.add(user)

async def get_user(username :str):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
# Messages -----------------------------------------------------------------------------------------------

async def add_message(sender : str, recipient : str, message : str, msg_id : str):
    async with async_session() as session:
        async with session.begin():
            encrypted_message = encrypt_message(key, message)
            msg = Message(msg_id=str(msg_id), sender=sender, recipient=recipient, message=encrypted_message)
            session.add(msg)

async def fetch_undelivered(recipient : str):
    async with async_session() as session:
        result = await session.execute(select(Message).where(Message.recipient == recipient, Message.delivered == False))
        messages = result.scalars().all()
        for message in messages:
            message.delivered = True
        await session.commit()
        return messages

async def chat_history_load(user1 : str, user2 : str):
    async with async_session() as session:
        result = await session.execute(select(Message).where(
            ((Message.sender == user1) & (Message.recipient == user2)) | 
            ((Message.sender == user2) & (Message.recipient == user1))).order_by(Message.TIMESTAMP))
        return result.scalars().all()
    
async def fetch_chat_history(user1 : str, user2 : str) -> list:
    messages = await chat_history_load(user1, user2)
    chat_history = []

    for msg in messages:
        decrypted_text = decrypt_message(key, msg.message)
        chat_history.append({
            "From" : msg.sender,
            "To" : msg.recipient,
            "msg" : decrypted_text,
            "timestamp" : msg.TIMESTAMP
        })
    return chat_history

async def fetch_contacts(current_username):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.username != current_username))
        users = result.scalars().all()
        return [
            {
                "username" : user.username,
                "onion" : user.onion,
                "email" : user.email
            }
            for user in users
        ]