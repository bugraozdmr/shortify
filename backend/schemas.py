from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from models import PostStatus

# ---------- SETTINGS SCHEMAS ----------

class SettingsBase(BaseModel):
    is_auto_upload: bool
    allowed_upload_start_time: str
    allowed_upload_end_time: str
    ai_provider: str
    ai_model: str
    ai_system_prompt: Optional[str] = None
    default_voice_male: str
    default_voice_female: str
    font_style: str
    font_size: int
    subtitle_outline: float
    youtube_privacy: str
    youtube_category_id: str
    youtube_tags: str

class SettingsUpdate(SettingsBase):
    pass

class SettingsOut(SettingsBase):
    id: int
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# ---------- POST SCHEMAS ----------

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
    video_path: Optional[str] = None
    youtube_video_id: Optional[str] = None
    youtube_url: Optional[str] = None
    youtube_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

from enum import Enum

class GenerateMode(str, Enum):
    auto = "auto"
    manual = "manual"

class GenerateRequest(BaseModel):
    # 'auto' seçilirse Reddit'ten çeker. 'manual' seçilirse custom_text'i kullanır.
    mode: GenerateMode = GenerateMode.auto
    custom_text: Optional[str] = None
