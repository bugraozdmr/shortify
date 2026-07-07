import os
import pytest
from pipeline.youtube import upload_video_to_youtube

def test_upload_youtube_unlisted():
    """
    Test uploading a video to YouTube as unlisted.
    Requires CLIENT_ID and CLIENT_SECRET in .env and an interactive browser login the first time.
    """
    video_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "videos", "test_output.mp4")
    
    if not os.path.exists(video_path):
        pytest.skip(f"Test video not found at {video_path}. Run test_render.py first.")
        
    title = "Test Shortify Otomatik Yükleme 🚀 #shorts"
    description = "Bu video Shortify projesi test otomasyonu tarafından yüklenmiştir."
    tags = ["test", "shortify", "python", "automation", "shorts"]
    
    # "unlisted" olarak yüklüyoruz, abonelere bildirim gitmez ve aramalarda çıkmaz.
    video_id = upload_video_to_youtube(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        privacy_status="unlisted"
    )
    
    assert video_id is not None
    assert isinstance(video_id, str)
    assert len(video_id) > 5
