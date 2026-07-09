from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from utils.config import config
from sqlalchemy.pool import NullPool

DATABASE_URL = config.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True, poolclass=NullPool)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session
