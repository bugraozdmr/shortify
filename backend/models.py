import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Boolean, Float
from sqlalchemy.sql import func
from database import Base

class PostStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), default="reddit") # reddit, custom vs
    source_id = Column(String(100), unique=True, index=True, nullable=False) # reddit post id
    subreddit = Column(String(100), nullable=True)
    author = Column(String(100), nullable=True)
    upvotes = Column(Integer, default=0)
    
    title = Column(String(255), nullable=False)
    original_text = Column(Text, nullable=False)
    
    ai_text = Column(Text, nullable=True)
    ai_prompt_used = Column(Text, nullable=True)
    
    voice_used = Column(String(100), nullable=True)
    music_used = Column(String(255), nullable=True)
    bg_video_used = Column(String(255), nullable=True)
    
    status = Column(Enum(PostStatus), default=PostStatus.pending)
    error_message = Column(Text, nullable=True)
    
    video_path = Column(String(512), nullable=True)
    
    # YouTube Integration
    youtube_video_id = Column(String(100), nullable=True)
    youtube_url = Column(String(512), nullable=True)
    youtube_status = Column(String(50), default="pending") # pending, uploaded, failed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)

class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    
    # Pipeline Settings
    is_auto_upload = Column(Boolean, default=False)
    allowed_upload_start_time = Column(String(5), default="18:00")
    allowed_upload_end_time = Column(String(5), default="22:00")
    
    # AI Settings
    ai_provider = Column(String(50), default="gemini")
    ai_model = Column(String(100), default="gemini-2.5-flash")
    ai_system_prompt = Column(Text, nullable=True)
    
    # TTS & Media Settings
    default_voice_male = Column(String(100), default="tr-TR-AhmetNeural")
    default_voice_female = Column(String(100), default="tr-TR-EmelNeural")
    font_style = Column(String(100), default="Impact")
    font_size = Column(Integer, default=20)
    subtitle_outline = Column(Float, default=2.5)
    
    # YouTube Upload Settings
    youtube_privacy = Column(String(20), default="unlisted") # public, private, unlisted
    youtube_category_id = Column(String(10), default="24")
    youtube_tags = Column(String(255), default="shorts,story,reddit,ai")
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
