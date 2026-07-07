from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import Settings
from schemas import SettingsOut, SettingsUpdate

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/", response_model=SettingsOut)
async def get_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Settings).limit(1))
    settings = result.scalars().first()
    
    if not settings:
        # Eğer ayar yoksa varsayılanı oluştur
        settings = Settings()
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
        
    return settings

@router.put("/", response_model=SettingsOut)
async def update_settings(settings_data: SettingsUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Settings).limit(1))
    settings = result.scalars().first()
    
    if not settings:
        settings = Settings()
        db.add(settings)
        
    for key, value in settings_data.model_dump().items():
        setattr(settings, key, value)
        
    await db.commit()
    await db.refresh(settings)
    return settings
