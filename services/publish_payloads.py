from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from services.assets_store import PropertyPaths, ensure_dir, read_meta, get_property_paths


@dataclass
class PublishResult:
    ok: bool
    messages: List[str]
    created_files: List[str]


def _write_json(path: Path, data: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def _get_best_asset(paths: PropertyPaths, patterns: List[str]) -> Optional[str]:
    # patterns order matters; return first existing file path (as posix)
    for pat in patterns:
        # Check in processed/thumbs, processed/videos, raw/videos etc depending on passed pattern
        # The glob pattern should be relative to base or absolute if we can handle it
        # But glob() works on the directory.
        # Let's assume patterns are like "processed/videos/*.mp4"
        
        # We need to handle the glob correctly. 
        # paths.base is the property dir.
        parts = pat.split('/')
        if len(parts) > 1:
            subdir = paths.base / parts[0]
            if len(parts) > 2:
                subdir = subdir.joinpath(*parts[1:-1])
            search_pat = parts[-1]
            
            if subdir.exists():
                for p in sorted(subdir.glob(search_pat)):
                    if p.is_file():
                        return p.as_posix()
    return None


def build_common_text(meta: Dict) -> Dict[str, str]:
    title = (meta.get("title") or "저평가 추천 매물").strip()
    address = (meta.get("address") or "").strip()
    gap = str(meta.get("market_gap_percent") or "").strip()
    price = str(meta.get("price") or "").strip()
    area = str(meta.get("area") or "").strip()
    rlink = (meta.get("reservation_link") or "").strip()

    badge = f"📉 실거래가 대비 저평가 {gap}%" if gap else "📉 실거래가 대비 저평가 추천"
    line_price = " · ".join([s for s in [f"{area}㎡" if area else "", f"{price}" if price else ""] if s]).strip()

    # 핵심 메시지(짧고 공유 친화)
    short_hook = f"{badge}\n{title}"
    if address:
        short_hook += f"\n📍 {address}"
    if line_price:
        short_hook += f"\n💰 {line_price}"
    if rlink:
        short_hook += f"\n✅ 상담/예약: {rlink}"

    # 해시태그(기본)
    tags = ["#저평가매물", "#실거래가", "#부동산", "#강남", "#상담예약", "#숏츠"]
    if address:
        # 지역명이 들어가면 태그로도 활용
        tags.append("#" + address.replace(" ", ""))

    return {
        "title": title,
        "address": address,
        "badge": badge,
        "line_price": line_price,
        "reservation_link": rlink,
        "short_hook": short_hook,
        "hashtags": " ".join(tags[:12]),
    }


def make_youtube_payload(paths: PropertyPaths) -> PublishResult:
    meta = read_meta(paths)
    text = build_common_text(meta)

    video_path = _get_best_asset(paths, ["processed/videos/*.mp4", "raw/videos/*.mp4"])
    thumb_path = _get_best_asset(paths, ["processed/thumbs/yt_shorts_thumb_*.jpg", "processed/thumbs/yt_thumb_*.jpg"])

    # 유튜브용 제목/설명(검색+예약 전환 중심)
    title = f"{text['title']} | {text['badge']}"
    if text["line_price"]:
        title = (title + f" | {text['line_price']}")[:98]

    desc_lines = [
        text["short_hook"],
        "",
        "—",
        "📌 핵심 포인트",
        f"- {text['badge']}",
    ]
    if text["address"]:
        desc_lines.append(f"- 위치: {text['address']}")
    if text["line_price"]:
        desc_lines.append(f"- 조건: {text['line_price']}")
    if text["reservation_link"]:
        desc_lines += [
            "",
            "📞 빠른 상담/예약",
            text["reservation_link"],
        ]
    desc_lines += [
        "",
        "🔎 해시태그",
        text["hashtags"],
    ]

    payload = {
        "property_id": paths.property_id,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "type": "youtube_shorts",
        "video_file": video_path or "",
        "thumbnail_file": thumb_path or "",
        "title": title,
        "description": "\n".join(desc_lines),
        "tags": [t.strip("#") for t in text["hashtags"].split()],
        "privacyStatus": "unlisted",  # 기본은 비공개/일부공개 권장
        "categoryId": "22",  # People & Blogs (임시)
    }

    out = paths.publish_youtube / "upload_payload.json"
    _write_json(out, payload)

    ok = True
    msgs = [
        f"유튜브 payload 생성: {out.name}",
        f"- video_file: {payload['video_file'] or '(없음)'}",
        f"- thumbnail_file: {payload['thumbnail_file'] or '(없음)'}",
    ]
    return PublishResult(ok, msgs, [out.as_posix()])


def make_kakao_payload(paths: PropertyPaths) -> PublishResult:
    meta = read_meta(paths)
    text = build_common_text(meta)

    kakao_img = _get_best_asset(paths, ["processed/thumbs/kakao_*.jpg", "processed/thumbs/*.jpg", "processed/photos/cover_*.jpg"])

    # 카카오 공유 문구는 더 짧게(대화형)
    msg_lines = [
        f"{text['badge']}",
        f"🏠 {text['title']}",
    ]
    if text["address"]:
        msg_lines.append(f"📍 {text['address']}")
    if text["line_price"]:
        msg_lines.append(f"💰 {text['line_price']}")
    if text["reservation_link"]:
        msg_lines.append(f"✅ 상담/예약 링크\n{text['reservation_link']}")
    msg_lines.append(text["hashtags"])

    payload = {
        "property_id": paths.property_id,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "type": "kakao_share",
        "image_file": kakao_img or "",
        "message": "\n".join(msg_lines),
        "button": {
            "title": "상담/예약하기",
            "url": text["reservation_link"] or "",
        },
    }

    out = paths.publish_kakao / "message_payload.json"
    _write_json(out, payload)

    msgs = [
        f"카카오 payload 생성: {out.name}",
        f"- image_file: {payload['image_file'] or '(없음)'}",
    ]
    return PublishResult(True, msgs, [out.as_posix()])


def make_sns_payloads(paths: PropertyPaths) -> PublishResult:
    meta = read_meta(paths)
    text = build_common_text(meta)

    # 인스타/페북 등(캡션)
    caption = text["short_hook"] + "\n\n" + text["hashtags"]
    
    # helper for finding files
    img_file = _get_best_asset(paths, ["processed/thumbs/kakao_*.jpg", "processed/photos/cover_*.jpg"])
    vid_file = _get_best_asset(paths, ["processed/videos/*.mp4"])
    
    insta = {
        "property_id": paths.property_id,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "type": "instagram",
        "caption": caption,
        "image_file": img_file or "",
        "video_file": vid_file or "",
    }

    # 네이버 블로그 HTML(심플)
    html = f"""
<div style="font-family: Pretendard, Apple SD Gothic Neo, sans-serif; line-height:1.6;">
  <h2>{text['title']}</h2>
  <p><b>{text['badge']}</b></p>
  <p>📍 {text['address']}</p>
  <p>💰 {text['line_price']}</p>
  <p style="margin-top:14px;">
    ✅ 상담/예약: <a href="{text['reservation_link']}" target="_blank">{text['reservation_link']}</a>
  </p>
  <hr/>
  <p>{text['hashtags']}</p>
</div>
""".strip()

    out1 = paths.publish_sns / "insta_payload.json"
    out2 = paths.publish_sns / "naverblog_payload.html"
    _write_json(out1, insta)
    _write_text(out2, html)

    msgs = [
        f"SNS payload 생성: {out1.name}, {out2.name}",
        f"- insta image_file: {insta['image_file'] or '(없음)'}",
        f"- insta video_file: {insta['video_file'] or '(없음)'}",
    ]
    return PublishResult(True, msgs, [out1.as_posix(), out2.as_posix()])


def run_all_publish_payloads(paths: PropertyPaths) -> PublishResult:
    msgs: List[str] = []
    created: List[str] = []

    r1 = make_youtube_payload(paths)
    msgs += ["[YouTube] " + m for m in r1.messages]
    created += r1.created_files

    r2 = make_kakao_payload(paths)
    msgs += ["[Kakao] " + m for m in r2.messages]
    created += r2.created_files

    r3 = make_sns_payloads(paths)
    msgs += ["[SNS] " + m for m in r3.messages]
    created += r3.created_files

    ok = r1.ok and r2.ok and r3.ok
    return PublishResult(ok, msgs, created)
