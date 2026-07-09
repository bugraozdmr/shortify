from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from loguru import logger

if not os.path.exists("logs"):
    os.makedirs("logs")

logger.add(
    "logs/app.log",
    rotation="5 MB",
    retention=2,
    encoding="utf-8",
    level="INFO",
    backtrace=True,
    diagnose=True
)

from core.database import SessionLocal
from sqlalchemy.future import select

from routers import posts, settings, generate, stream, system, tasks
from services.scheduler import start_scheduler, stop_scheduler
from services.auto_generator import start as start_auto_gen, stop as stop_auto_gen
from fastapi.staticfiles import StaticFiles
from utils.config import config

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    start_auto_gen()
    yield
    stop_auto_gen()
    stop_scheduler()

APP_TYPE = config.APP_TYPE

if APP_TYPE == "PRODUCTION":
    app = FastAPI(title="Softinger Shorts API", version="1.0.0", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
else:
    app = FastAPI(title="Softinger Shorts API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Geliştirme aşamasında herkese açık, production'da spesifik domain girilmeli
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router)
app.include_router(posts.router)
app.include_router(settings.router)
app.include_router(generate.router)
app.include_router(stream.router)
app.include_router(tasks.router)

import os
if not os.path.exists("assets"):
    os.makedirs("assets")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")