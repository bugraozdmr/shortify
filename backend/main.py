from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from database import SessionLocal
from models import Settings
from sqlalchemy.future import select

from routers import posts, settings, generate, stream
from fastapi.staticfiles import StaticFiles

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Uygulama başlarken varsayılan ayarları veritabanına ekle (Seed)
    async with SessionLocal() as db:
        result = await db.execute(select(Settings).limit(1))
        current_settings = result.scalars().first()
        if not current_settings:
            print("Veritabanına varsayılan ayarlar (Seed) yükleniyor...")
            default_settings = Settings()
            db.add(default_settings)
            await db.commit()
    yield

APP_TYPE = os.getenv("APP_TYPE", "DEVELOPMENT").upper()

if APP_TYPE == "PRODUCTION":
    # Production'da swagger dokümantasyonunu gizle
    app = FastAPI(title="Softinger Shorts API", version="1.0.0", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
else:
    app = FastAPI(title="Softinger Shorts API", version="1.0.0", lifespan=lifespan)

# CORS ayarları (Next.js Frontend'in erişebilmesi için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Geliştirme aşamasında herkese açık, production'da spesifik domain girilmeli
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotaların dahil edilmesi
app.include_router(posts.router)
app.include_router(settings.router)
app.include_router(generate.router)
app.include_router(stream.router)

# Statik dosyaları dışarıya açma (Videoları izleyebilmek için)
import os
if not os.path.exists("assets"):
    os.makedirs("assets")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

@app.get("/")
def read_root():
    return {"message": "Video Pipeline API Çalışıyor! 🚀 Dökümantasyon için /docs adresine gidin."}

@app.get("/health")
def health_check():
    return {"status": "success", "message": "Backend is healthy and running."}