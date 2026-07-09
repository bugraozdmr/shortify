from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
import os
from datetime import datetime, timezone
from core.database import get_db
from core.models import Post
from core.schemas import PostOut, PaginatedPostsOut, PostUpdate
from typing import List, Optional

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("/", response_model=PaginatedPostsOut)
async def get_posts(
    skip: int = 0, 
    limit: int = 20, 
    status: Optional[str] = None,
    youtube_status: Optional[str] = None,
    sort_by: str = "desc",
    db: AsyncSession = Depends(get_db)
):
    conditions = [Post.deleted_at.is_(None)]
    
    if status and status.lower() != "all":
        conditions.append(Post.status == status)
        
    if youtube_status and youtube_status.lower() != "all":
        if youtube_status.lower() == "published":
            conditions.append(Post.youtube_status == "uploaded")
        elif youtube_status.lower() == "unpublished":
            conditions.append(Post.youtube_status != "uploaded")

    query = select(Post)
    count_query = select(func.count(Post.id))
    
    for condition in conditions:
        query = query.filter(condition)
        count_query = count_query.filter(condition)

    # Sorting
    if sort_by.lower() == "asc":
        query = query.order_by(Post.created_at.asc())
    else:
        query = query.order_by(Post.created_at.desc())
        
    # Count total matching records
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Pagination
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return {"total": total, "items": items}

@router.get("/{post_id}", response_model=PostOut)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).filter(Post.id == post_id, Post.deleted_at.is_(None)))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.put("/{post_id}", response_model=PostOut)
async def update_post(post_id: int, post_update: PostUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).filter(Post.id == post_id, Post.deleted_at.is_(None)))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    if post_update.youtube_title is not None:
        post.youtube_title = post_update.youtube_title
    if post_update.youtube_description is not None:
        post.youtube_description = post_update.youtube_description
    if post_update.youtube_tags is not None:
        post.youtube_tags = post_update.youtube_tags
    if post_update.scheduled_at is not None:
        post.scheduled_at = post_update.scheduled_at
        
    await db.commit()
    await db.refresh(post)
    return post

@router.post("/{post_id}/publish")
async def publish_post(
    post_id: int,
    scheduled_at: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Post).filter(Post.id == post_id, Post.deleted_at.is_(None)))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    if not post.video_path or not os.path.exists(post.video_path):
         raise HTTPException(status_code=400, detail="Video file not found")

    if scheduled_at:
        post.scheduled_at = scheduled_at
        message = "Post scheduled for publishing"
        await db.commit()
        await db.refresh(post)
        return {"message": message, "scheduled_at": scheduled_at.isoformat()}
         
    post.youtube_status = "uploaded"
    post.published_at = func.now()
    
    await db.commit()
    await db.refresh(post)
    return {"message": "Post published successfully", "youtube_status": "uploaded"}

@router.delete("/{post_id}")
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).filter(Post.id == post_id, Post.deleted_at.is_(None)))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Post deleted successfully"}
