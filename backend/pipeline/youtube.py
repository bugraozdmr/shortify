import os
import sys
from loguru import logger
from sqlalchemy.future import select
from core.database import SessionLocal
from core.models import Setting
import asyncio
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def _get_youtube_settings():
    async def fetch():
        async with SessionLocal() as db:
            result = await db.execute(select(Setting).where(Setting.key.in_([
                "youtube_client_id", "youtube_client_secret", "youtube_redirect_uri"
            ])))
            rows = result.scalars().all()
            settings = {s.key: s.value.strip('"') if isinstance(s.value, str) else s.value for s in rows}
            return {
                "client_id": settings.get("youtube_client_id", ""),
                "client_secret": settings.get("youtube_client_secret", ""),
                "redirect_uri": settings.get("youtube_redirect_uri", "http://localhost:8080/")
            }
    
    return asyncio.run(fetch())

def get_authenticated_service():
    creds = None
    # Token dosyasını assets altına kaydedeceğiz
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    token_path = os.path.join(assets_dir, 'token.json')
    
    # Mevcut bir token var mı?
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # Token yoksa veya geçersizse yenile veya yeniden giriş yap
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            settings = _get_youtube_settings()
            client_id = settings["client_id"]
            client_secret = settings["client_secret"]
            
            if not client_id or not client_secret:
                raise ValueError("youtube_client_id veya youtube_client_secret veritabanında bulunamadı!")
                
            from urllib.parse import urlparse
            redirect_uri = settings["redirect_uri"]
            parsed_uri = urlparse(redirect_uri)
            port = parsed_uri.port or 8080

            client_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            }
            # Tarayıcıda yetkilendirme akışını başlat
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=port)
        
        # Token'ı diske kaydet (sonraki girişler için)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            
    return build('youtube', 'v3', credentials=creds)

def upload_video_to_youtube(video_path: str, title: str, description: str, tags: list = None, category_id: str = "24", privacy_status: str = "public", publish_at=None):
    """
    Belirtilen videoyu YouTube'a yükler.
    category_id: 24 (Entertainment) veya 22 (People & Blogs)
    privacy_status: 'public', 'private', 'unlisted'
    publish_at: datetime object for scheduled publish. If provided, privacy_status must be 'private'.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video bulunamadı: {video_path}")

    youtube = get_authenticated_service()

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags or ["shorts", "story", "reddit", "ai"],
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }
    
    if publish_at:
        body['status']['privacyStatus'] = 'private'
        from datetime import timezone
        if publish_at.tzinfo is None:
            publish_at = publish_at.replace(tzinfo=timezone.utc)
        body['status']['publishAt'] = publish_at.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )

    logger.info(f"YouTube yüklemesi başlıyor: {video_path}")
    response = None
    while response is None:
        status, response = insert_request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            sys.stdout.write(f"\rYükleniyor: {progress}%")
            sys.stdout.flush()

    logger.info(f"Yükleme Tamamlandı! Video ID: {response['id']} - https://youtu.be/{response['id']}")
    
    return response['id']
