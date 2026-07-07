import os
import sys
from dotenv import load_dotenv

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# .env dosyasını yükle
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

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
            client_id = os.getenv("CLIENT_ID")
            client_secret = os.getenv("CLIENT_SECRET")
            
            if not client_id or not client_secret:
                raise ValueError("CLIENT_ID veya CLIENT_SECRET .env dosyasında bulunamadı!")
                
            client_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:8080/"]
                }
            }
            # Tarayıcıda yetkilendirme akışını başlat
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=8080)
        
        # Token'ı diske kaydet (sonraki girişler için)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            
    return build('youtube', 'v3', credentials=creds)

def upload_video_to_youtube(video_path: str, title: str, description: str, tags: list = None, category_id: str = "24", privacy_status: str = "unlisted"):
    """
    Belirtilen videoyu YouTube'a yükler.
    category_id: 24 (Entertainment) veya 22 (People & Blogs)
    privacy_status: 'public', 'private', 'unlisted'
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

    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )

    print(f"\nYouTube yüklemesi başlıyor: {video_path}")
    response = None
    while response is None:
        status, response = insert_request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            sys.stdout.write(f"\rYükleniyor: {progress}%")
            sys.stdout.flush()

    print(f"\n\n✅ Yükleme Tamamlandı! Video ID: {response['id']}")
    print(f"🔗 Video Linki: https://youtu.be/{response['id']}")
    
    return response['id']
