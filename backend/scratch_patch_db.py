import asyncio
import json
from core.database import SessionLocal
import sqlalchemy

async def main():
    async with SessionLocal() as db:
        res = await db.execute(sqlalchemy.text("SELECT value FROM settings WHERE `key` = 'api_keys'"))
        row = res.fetchone()
        keys = json.loads(row[0]) if row else {}
        if "openrouter" not in keys:
            keys["openrouter"] = ""
            await db.execute(
                sqlalchemy.text("UPDATE settings SET value = :v WHERE `key` = 'api_keys'"),
                {"v": json.dumps(keys)}
            )
            await db.commit()
            print("DB 'api_keys' satırına openrouter eklendi.")
        else:
            print("openrouter zaten mevcut.")

if __name__ == "__main__":
    asyncio.run(main())