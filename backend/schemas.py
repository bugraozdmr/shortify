from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from models import PostStatus

# ---------- SETTINGS SCHEMAS ----------

from typing import Dict, Any

SettingsPayload = Dict[str, Any]

# ---------- POST SCHEMAS ----------

class PostUpdate(BaseModel):
    youtube_title: Optional[str] = None
    youtube_description: Optional[str] = None
    youtube_tags: Optional[str] = None
    scheduled_at: Optional[datetime] = None

class PostOut(BaseModel):
    id: int
    source: str
    source_id: str
    subreddit: Optional[str] = None
    author: Optional[str] = None
    upvotes: int
    title: str
    original_text: str
    ai_text: Optional[str] = None
    ai_prompt_used: Optional[str] = None
    voice_used: Optional[str] = None
    music_used: Optional[str] = None
    bg_video_used: Optional[str] = None
    status: PostStatus
    error_message: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    video_path: Optional[str] = None
    youtube_video_id: Optional[str] = None
    youtube_url: Optional[str] = None
    youtube_status: str
    youtube_title: Optional[str] = None
    youtube_description: Optional[str] = None
    youtube_tags: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PaginatedPostsOut(BaseModel):
    total: int
    items: list[PostOut]

from enum import Enum

class GenerateMode(str, Enum):
    auto = "auto"
    manual = "manual"

class GenerateRequest(BaseModel):
    # 'auto' seçilirse Reddit'ten çeker. 'manual' seçilirse custom_text'i kullanır.
    mode: GenerateMode = GenerateMode.auto
    custom_text: Optional[str] = None
