from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

import os
import shutil

db_url = settings.database_url

if os.environ.get("VERCEL") == "1":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    src_db = os.path.join(project_root, "banco_precos.db")
    dest_db = "/tmp/banco_precos.db"
    if os.path.exists(src_db) and not os.path.exists(dest_db):
        try:
            shutil.copy2(src_db, dest_db)
        except Exception as e:
            print(f"Erro ao copiar o banco de dados para /tmp: {e}")
    db_url = "sqlite+aiosqlite:////tmp/banco_precos.db"

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    db_url,
    connect_args=connect_args,
    echo=settings.debug
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
StandardBase = Base # helper name for seeding scripts
