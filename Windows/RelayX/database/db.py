import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DB_path = os.path.join("Windows", "RelayX", "database", "RelayX.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_path}"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()
