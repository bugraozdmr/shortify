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
    
    youtube_title = Column(String(100), nullable=True)
    youtube_description = Column(Text, nullable=True)
    youtube_tags = Column(String(500), nullable=True)
    
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)

class Setting(Base):
    __tablename__ = "settings"

    key = Column(String(100), primary_key=True, index=True)
    value = Column(Text, nullable=False) # JSON encoded string
    category = Column(String(50), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
