import asyncio
import sqlalchemy
from core.database import SessionLocal

async def add_col():
    async with SessionLocal() as db:
        try:
            await db.execute(sqlalchemy.text('ALTER TABLE posts ADD COLUMN comments JSON NULL;'))
            await db.commit()
            print('Column added')
        except Exception as e:
            print("Already exists or error:", e)

if __name__ == "__main__":
    asyncio.run(add_col())
