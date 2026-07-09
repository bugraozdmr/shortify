import os
import subprocess
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import StreamingResponse, FileResponse

router = APIRouter(
    prefix="/stream",
    tags=["stream"]
)

CHUNK_SIZE = 1024 * 1024 * 2

@router.get("/thumbnail/{video_name}")
async def get_thumbnail(video_name: str):
    video_path = os.path.join("assets", "videos", video_name)
    
    if not os.path.exists(video_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
        
    thumbnails_dir = os.path.join("assets", "thumbnails")
    os.makedirs(thumbnails_dir, exist_ok=True)
    
    thumb_name = video_name.rsplit('.', 1)[0] + ".jpg"
    thumb_path = os.path.join(thumbnails_dir, thumb_name)
    
    if not os.path.exists(thumb_path):
        try:
            subprocess.run([
                "ffmpeg", "-i", video_path, "-ss", "00:00:01.000", 
                "-vframes", "1", thumb_path, "-y"
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating thumbnail: {str(e)}")
            
    if not os.path.exists(thumb_path):
        raise HTTPException(status_code=404, detail="Thumbnail could not be generated")
        
    return FileResponse(thumb_path, media_type="image/jpeg")

@router.get("/video/{video_name}")
async def stream_video(video_name: str, request: Request):
    video_path = os.path.join("assets", "videos", video_name)
    
    if not os.path.exists(video_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    file_size = os.stat(video_path).st_size
    range_header = request.headers.get("range")

    if not range_header:
        headers = {
            "Content-Length": str(file_size),
            "Accept-Ranges": "bytes",
            "Content-Type": "video/mp4",
        }
        
        def file_iterator_full(file_path: str, chunk_size: int):
            with open(file_path, "rb") as f:
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    yield data

        return StreamingResponse(
            file_iterator_full(video_path, CHUNK_SIZE), 
            headers=headers, 
            media_type="video/mp4"
        )

    try:
        range_str = range_header.strip().split("=")[1]
        start_str, end_str = range_str.split("-")
        start = int(start_str)
        end = int(end_str) if end_str else file_size - 1
    except ValueError:
        raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    end = min(end, file_size - 1)
    
    length = end - start + 1

    def file_iterator_partial(file_path: str, start: int, end: int, chunk_size: int):
        with open(file_path, "rb") as f:
            f.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                bytes_to_read = min(chunk_size, remaining)
                data = f.read(bytes_to_read)
                if not data:
                    break
                remaining -= len(data)
                yield data

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(length),
        "Content-Type": "video/mp4",
        "Cache-Control": "public, max-age=3600"
    }

    return StreamingResponse(
        file_iterator_partial(video_path, start, end, CHUNK_SIZE),
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        headers=headers,
        media_type="video/mp4"
    )
