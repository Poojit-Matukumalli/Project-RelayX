from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func
import asyncio
from RelayX.database.db import Base, engine

class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True)
    onion = Column(String, nullable=False)
    email = Column(String)
    last_seen = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    msg_id = Column(String, nullable=False)
    sender = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    message = Column(String, nullable=False)
    TIMESTAMP = Column(TIMESTAMP, default=func.now())
    delivered = Column(Boolean, default=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_db())