from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from worker import celery_app
from loguru import logger
from typing import List, Dict, Any

import os
import json
from redis.asyncio import Redis

router = APIRouter(prefix="/tasks", tags=["Tasks"])

class TaskStatusResponse(BaseModel):
    active: List[Dict[str, Any]]
    reserved: List[Dict[str, Any]]
    scheduled: List[Dict[str, Any]]

@router.get("/status", response_model=TaskStatusResponse)
async def get_task_status():
    try:
        i = celery_app.control.inspect()
        
        # inspect() metotları bazen worker kapalıyken None dönebilir.
        active = i.active() or {}
        reserved = i.reserved() or {}
        scheduled = i.scheduled() or {}
        
        # Her bir worker altındaki listeleri tek bir düz listeye birleştir
        active_list = []
        for worker_tasks in active.values():
            active_list.extend(worker_tasks)
            
        reserved_list = []
        for worker_tasks in reserved.values():
            reserved_list.extend(worker_tasks)
            
        scheduled_list = []
        for worker_tasks in scheduled.values():
            scheduled_list.extend(worker_tasks)

        return {
            "active": active_list,
            "reserved": reserved_list,
            "scheduled": scheduled_list
        }
    except Exception as e:
        logger.error(f"Error fetching task status: {e}")
        raise HTTPException(status_code=500, detail="Celery worker'a bağlanılamadı. Worker çalışıyor mu?")

@router.delete("/purge")
async def purge_tasks():
    try:
        cleared_count = celery_app.control.purge()
        return {"message": f"Kuyruk tamamen temizlendi.", "cleared_tasks_count": cleared_count}
    except Exception as e:
        logger.error(f"Error purging tasks: {e}")
        raise HTTPException(status_code=500, detail="Görevler silinirken hata oluştu.")

@router.delete("/{task_id}")
async def revoke_task(task_id: str):
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {"message": f"Görev {task_id} iptal edildi (Eğer çalışıyorsa zorla durduruldu)."}
    except Exception as e:
        logger.error(f"Error revoking task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Görev iptal edilemedi: {str(e)}")


from utils.config import config

def get_redis_client():
    redis_url = config.REDIS_URL
    return Redis.from_url(redis_url, decode_responses=True)

@router.get("/redis_results")
async def get_redis_results():
    try:
        client = get_redis_client()
        keys = await client.keys("celery-task-meta-*")
        
        # Eğer çok fazlaysa sadece sayısını ve ilk 50'sini dön
        sample_keys = keys[:50]
        results = []
        for key in sample_keys:
            val = await client.get(key)
            if val:
                try:
                    data = json.loads(val)
                    results.append({"task_id": data.get("task_id"), "status": data.get("status")})
                except:
                    results.append({"key": key, "status": "unknown"})
                    
        await client.close()
        
        return {
            "total_count": len(keys),
            "sample_results": results
        }
    except Exception as e:
        logger.error(f"Error reading redis results: {e}")
        raise HTTPException(status_code=500, detail="Redis'e bağlanılamadı.")

@router.delete("/redis_results/clean")
async def clean_redis_results():
    try:
        client = get_redis_client()
        keys = await client.keys("celery-task-meta-*")
        
        deleted = 0
        if keys:
            deleted = await client.delete(*keys)
            
        await client.close()
        
        return {"message": "Redis geçmiş görev sonuçları temizlendi.", "deleted_count": deleted}
    except Exception as e:
        logger.error(f"Error cleaning redis results: {e}")
        raise HTTPException(status_code=500, detail="Redis temizlenirken hata oluştu.")
