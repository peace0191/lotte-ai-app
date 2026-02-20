from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

# These are google libs which should be installed
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
except ImportError:
    # Fallback/mock if libs are missing, though requirements should have them
    pass

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

KEYS_DIR = Path("assets/system/keys")
CLIENT_SECRET = KEYS_DIR / "youtube_client_secret.json"
TOKEN_FILE = KEYS_DIR / "youtube_token.json"


def _ensure_keys_dir():
    KEYS_DIR.mkdir(parents=True, exist_ok=True)


def get_youtube_service() -> Any:
    """
    로컬/서버에서 OAuth 토큰을 발급/저장 후, YouTube API 서비스 객체를 반환합니다.
    (InstalledAppFlow 사용: 최초 1회 브라우저 인증 필요)
    """
    _ensure_keys_dir()

    if not CLIENT_SECRET.exists():
        raise FileNotFoundError(f"OAuth 파일이 없습니다: {CLIENT_SECRET.as_posix()}")

    creds: Optional[Credentials] = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # 최초 1회: 브라우저 인증 필요
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    return build("youtube", "v3", credentials=creds)


def upload_video_from_payload(payload_path: Path) -> Dict[str, Any]:
    """
    publish/youtube/upload_payload.json을 읽어 실제 업로드 수행.
    반환: 업로드 결과(영상ID 등)
    """
    payload = json.loads(payload_path.read_text(encoding="utf-8"))

    video_file = payload.get("video_file", "")
    thumb_file = payload.get("thumbnail_file", "")
    title = payload.get("title", "Untitled")
    description = payload.get("description", "")
    tags = payload.get("tags", [])
    privacy = payload.get("privacyStatus", "unlisted")
    category_id = payload.get("categoryId", "22")

    if not video_file or not Path(video_file).exists():
        raise FileNotFoundError(f"업로드할 video_file이 없거나 경로가 잘못되었습니다: {video_file}")

    youtube = get_youtube_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    # resumable 업로드 진행
    response = None
    while response is None:
        status, response = request.next_chunk()
        # status.progress()가 있을 때 진행률 표시 가능

    video_id = response.get("id")

    # 썸네일 업로드(선택)
    if video_id and thumb_file and Path(thumb_file).exists():
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumb_file)
            ).execute()
        except Exception:
            # Thumb upload might fail if not verified account etc. Don't block.
            pass

    return {
        "ok": True,
        "video_id": video_id,
        "watch_url": f"https://www.youtube.com/watch?v={video_id}" if video_id else "",
        "response": response,
    }
