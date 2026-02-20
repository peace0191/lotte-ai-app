from __future__ import annotations

import json
import math
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from services.assets_store import PropertyPaths, read_meta, ensure_dir


BRANDING_DIR = Path("assets") / "branding"
WATERMARK_DEFAULT = BRANDING_DIR / "watermark" / "wm_kr.png"
TEMPLATE_KAKAO = BRANDING_DIR / "templates" / "kakao_card_01.png"
TEMPLATE_YT = BRANDING_DIR / "templates" / "youtube_thumb_01.png"
FONT_DEFAULT = BRANDING_DIR / "fonts" / "Pretendard-Regular.ttf"


# -------------------------
# Helpers
# -------------------------
def _load_image(path: Path) -> Optional[Image.Image]:
    try:
        if path.exists():
            return Image.open(path).convert("RGBA")
        return None
    except Exception:
        return None


def _save_jpg(img: Image.Image, out_path: Path, quality: int = 92) -> None:
    ensure_dir(out_path.parent)
    rgb = img.convert("RGB")
    rgb.save(out_path, format="JPEG", quality=quality, optimize=True)


def _save_png(img: Image.Image, out_path: Path) -> None:
    ensure_dir(out_path.parent)
    img.save(out_path, format="PNG", optimize=True)


def _fit_cover(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Center-crop to cover target aspect, then resize."""
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        # wider: crop left/right
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        box = (left, 0, left + new_w, src_h)
    else:
        # taller: crop top/bottom
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        box = (0, top, src_w, top + new_h)

    cropped = img.crop(box)
    return cropped.resize((target_w, target_h), Image.LANCZOS)


def _load_font(font_path: Path, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size=size)
    except Exception:
        pass
    return ImageFont.load_default()


def _draw_text_box(
    base: Image.Image,
    text_lines: List[str],
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    x: int,
    y: int,
    box_w: int,
    padding: int = 16,
    fill=(255, 255, 255, 255),
    box_fill=(0, 0, 0, 160),
    radius: int = 18,
) -> None:
    """Draw rounded rectangle + multiline text."""
    draw = ImageDraw.Draw(base, "RGBA")

    # measure
    line_heights = []
    max_line_w = 0
    for line in text_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        max_line_w = max(max_line_w, w)
        line_heights.append(h)

    content_w = min(box_w - padding * 2, max_line_w)
    content_h = sum(line_heights) + max(0, (len(text_lines) - 1) * 8)

    rect_w = content_w + padding * 2
    rect_h = content_h + padding * 2

    # rounded rect
    _rounded_rectangle(draw, (x, y, x + rect_w, y + rect_h), radius, fill=box_fill)

    # draw text
    ty = y + padding
    for i, line in enumerate(text_lines):
        draw.text((x + padding, ty), line, font=font, fill=fill)
        ty += line_heights[i] + 8


def _rounded_rectangle(draw: ImageDraw.ImageDraw, rect: Tuple[int, int, int, int], r: int, fill):
    x1, y1, x2, y2 = rect
    draw.rounded_rectangle(rect, radius=r, fill=fill)


def _apply_watermark(
    img: Image.Image,
    watermark: Optional[Image.Image],
    mode: str = "bottom_right",
    scale_ratio: float = 0.22,  # watermark width ratio of image width
    margin_ratio: float = 0.02,
) -> Image.Image:
    if watermark is None:
        return img

    base = img.copy().convert("RGBA")
    wm = watermark.copy().convert("RGBA")

    W, H = base.size
    target_w = int(W * scale_ratio)
    if target_w <= 10:
        return base

    # keep aspect
    wm_w, wm_h = wm.size
    scale = target_w / wm_w
    new_w = target_w
    new_h = max(1, int(wm_h * scale))
    wm = wm.resize((new_w, new_h), Image.LANCZOS)

    margin = int(min(W, H) * margin_ratio)

    if mode == "bottom_center":
        x = (W - new_w) // 2
        y = H - new_h - margin
    else:
        # bottom_right
        x = W - new_w - margin
        y = H - new_h - margin

    base.paste(wm, (x, y), wm)
    return base


# -------------------------
# Public API
# -------------------------
@dataclass
class PipelineResult:
    ok: bool
    messages: List[str]
    created_files: List[str]


def list_raw_photos(paths: PropertyPaths) -> List[Path]:
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    if not paths.raw_photos.exists():
        return []
    return sorted([p for p in paths.raw_photos.iterdir() if p.is_file() and p.suffix.lower() in exts])


def list_raw_videos(paths: PropertyPaths) -> List[Path]:
    exts = {".mp4", ".mov", ".m4v", ".avi", ".mkv"}
    if not paths.raw_videos.exists():
        return []
    return sorted([p for p in paths.raw_videos.iterdir() if p.is_file() and p.suffix.lower() in exts])


def process_photos_watermark_and_resize(
    paths: PropertyPaths,
    cover_size: Tuple[int, int] = (1200, 628),
    gallery_long_edge: int = 1600,
    watermark_path: Path = WATERMARK_DEFAULT,
) -> PipelineResult:
    msgs: List[str] = []
    created: List[str] = []

    photos = list_raw_photos(paths)
    if not photos:
        return PipelineResult(False, ["사진(raw)이 없습니다. 먼저 업로드하세요."], [])

    wm = _load_image(watermark_path)

    ensure_dir(paths.processed_photos)
    # cover
    try:
        first = Image.open(photos[0]).convert("RGBA")
        cover = _fit_cover(first, cover_size[0], cover_size[1])
        cover = _apply_watermark(cover, wm, mode="bottom_right")
        out = paths.processed_photos / f"cover_{cover_size[0]}x{cover_size[1]}.jpg"
        _save_jpg(cover, out)
        created.append(str(out))
        msgs.append(f"커버 생성: {out.name}")
    except Exception as e:
        msgs.append(f"커버 생성 실패: {e}")

    # gallery
    for idx, p in enumerate(photos, start=1):
        try:
            img = Image.open(p).convert("RGBA")
            w, h = img.size
            # resize by long edge
            if max(w, h) > gallery_long_edge:
                scale = gallery_long_edge / max(w, h)
                nw, nh = int(w * scale), int(h * scale)
                img = img.resize((nw, nh), Image.LANCZOS)
            img = _apply_watermark(img, wm, mode="bottom_right")
            out = paths.processed_photos / f"gallery_{idx:02d}_{img.size[0]}x{img.size[1]}.jpg"
            _save_jpg(img, out)
            created.append(str(out))
        except Exception as e:
            msgs.append(f"사진 처리 실패({p.name}): {e}")

    return PipelineResult(True, msgs, created)


def create_thumbnails(
    paths: PropertyPaths,
    yt_size: Tuple[int, int] = (1280, 720),
    shorts_size: Tuple[int, int] = (1080, 1920),
    kakao_size: Tuple[int, int] = (1080, 1080),
    watermark_path: Path = WATERMARK_DEFAULT,
) -> PipelineResult:
    msgs: List[str] = []
    created: List[str] = []
    meta = read_meta(paths)

    photos = list_raw_photos(paths)
    videos = list_raw_videos(paths)

    wm = _load_image(watermark_path)
    font_big = _load_font(FONT_DEFAULT, 56)
    font_mid = _load_font(FONT_DEFAULT, 40)

    # base image source priority: first photo, else frame from first video
    base_img: Optional[Image.Image] = None
    if photos:
        base_img = Image.open(photos[0]).convert("RGBA")
        msgs.append(f"썸네일 소스: 첫 사진({photos[0].name})")
    elif videos:
        try:
            from moviepy.editor import VideoFileClip  # type: ignore
            try:
                clip = VideoFileClip(str(videos[0]))
                t = 1.0 if clip.duration and clip.duration > 1.2 else 0.0
                frame = clip.get_frame(t)
                base_img = Image.fromarray(frame).convert("RGBA")
                msgs.append(f"썸네일 소스: 첫 영상 프레임({videos[0].name})")
                clip.close()
            except ImportError as ie:
                 msgs.append(f"영상 썸네일 실패(라이브러리): {ie}")
            except Exception as e:
                msgs.append(f"영상 썸네일 실패: {e}")
        except Exception as e:
            msgs.append(f"영상처리 라이브러리 오류: {e}")
            base_img = None

    if base_img is None:
        return PipelineResult(False, ["썸네일 생성 실패: 사진/영상이 없습니다."], [])

    title = (meta.get("title") or "추천 매물").strip()
    addr = (meta.get("address") or "").strip()
    gap = str(meta.get("market_gap_percent") or "").strip()
    price = str(meta.get("price") or "").strip()
    area = str(meta.get("area") or "").strip()

    line1 = title[:26]
    line2 = " · ".join([s for s in [addr, (f"저평가 {gap}% " if gap else "").strip()] if s])[:40]
    line3 = " · ".join([s for s in [f"{area}㎡" if area else "", f"{price}" if price else ""] if s])[:40]

    ensure_dir(paths.processed_thumbs)

    # Shorts thumb (9:16)
    try:
        img = _fit_cover(base_img, shorts_size[0], shorts_size[1])
        img = _apply_watermark(img, wm, mode="bottom_center", scale_ratio=0.28)
        _draw_text_box(
            img,
            [line1, line2, line3],
            font=font_mid,
            x=40,
            y=60,
            box_w=shorts_size[0] - 80,
            padding=18,
        )
        out = paths.processed_thumbs / "yt_shorts_thumb_01_1080x1920.jpg"
        _save_jpg(img, out)
        created.append(str(out))
        msgs.append(f"숏츠 썸네일 생성: {out.name}")
    except Exception as e:
        msgs.append(f"숏츠 썸네일 실패: {e}")

    # YouTube thumb (16:9) with template fallback
    try:
        template = _load_image(TEMPLATE_YT)
        img = _fit_cover(base_img, yt_size[0], yt_size[1])
        if template is not None:
            template = template.resize(yt_size, Image.LANCZOS)
            # overlay template (assumes transparency)
            img = Image.alpha_composite(img.convert("RGBA"), template)
        img = _apply_watermark(img, wm, mode="bottom_right", scale_ratio=0.22)
        _draw_text_box(
            img,
            [line1, line2],
            font=font_big,
            x=48,
            y=48,
            box_w=yt_size[0] - 96,
            padding=18,
        )
        out = paths.processed_thumbs / "yt_thumb_01_1280x720.jpg"
        _save_jpg(img, out)
        created.append(str(out))
        msgs.append(f"유튜브 썸네일 생성: {out.name}")
    except Exception as e:
        msgs.append(f"유튜브 썸네일 실패: {e}")

    # Kakao card (1:1) with template fallback
    try:
        template = _load_image(TEMPLATE_KAKAO)
        img = _fit_cover(base_img, kakao_size[0], kakao_size[1])
        if template is not None:
            template = template.resize(kakao_size, Image.LANCZOS)
            img = Image.alpha_composite(img.convert("RGBA"), template)
        img = _apply_watermark(img, wm, mode="bottom_center", scale_ratio=0.30)
        _draw_text_box(
            img,
            [line1, line2],
            font=font_mid,
            x=40,
            y=40,
            box_w=kakao_size[0] - 80,
            padding=16,
        )
        out = paths.processed_thumbs / "kakao_01_1080x1080.jpg"
        _save_jpg(img, out)
        created.append(str(out))
        msgs.append(f"카카오 카드 생성: {out.name}")
    except Exception as e:
        msgs.append(f"카카오 카드 실패: {e}")

    ok = any(Path(p).exists() for p in created)
    return PipelineResult(ok, msgs, created)


def render_shorts_video(
    paths: PropertyPaths,
    out_name: str = "short_01_1080x1920.mp4",
    target_size: Tuple[int, int] = (1080, 1920),
    max_duration: int = 25,
    min_duration: int = 15,
    watermark_path: Path = WATERMARK_DEFAULT,
) -> PipelineResult:
    msgs: List[str] = []
    created: List[str] = []

    videos = list_raw_videos(paths)
    photos = list_raw_photos(paths)
    wm_img = _load_image(watermark_path)

    out_path = paths.processed_videos / out_name
    ensure_dir(paths.processed_videos)

    try:
        # moviepy 기반
        from moviepy.editor import (  # type: ignore
            VideoFileClip,
            ImageClip,
            concatenate_videoclips,
            CompositeVideoClip,
        )
        from moviepy.video.fx.all import crop  # type: ignore

        W, H = target_size

        def watermark_clip(duration: float):
            if wm_img is None:
                return None
            wm = wm_img.copy().convert("RGBA")
            # make watermark width 30% of video width
            target_w = int(W * 0.30)
            scale = target_w / wm.size[0]
            nw, nh = target_w, max(1, int(wm.size[1] * scale))
            wm = wm.resize((nw, nh), Image.LANCZOS)
            # save temporary in memory by converting to numpy via ImageClip
            import numpy as np  # type: ignore
            arr = np.array(wm)
            clip = ImageClip(arr, transparent=True).set_duration(duration)
            x = (W - nw) // 2
            y = H - nh - int(H * 0.02)
            return clip.set_pos((x, y))

        if videos:
            # Use first video: center crop to 9:16 and resize
            vpath = videos[0]
            clip = VideoFileClip(str(vpath))
            dur = clip.duration or 0
            if dur <= 0:
                clip.close()
                return PipelineResult(False, [f"영상 duration을 읽지 못했습니다: {vpath.name}"], [])

            # limit duration
            use_dur = min(max_duration, dur)
            if use_dur < min_duration:
                msgs.append(f"경고: 영상 길이가 짧습니다({use_dur:.1f}s). 최소 {min_duration}s 권장")
            clip = clip.subclip(0, use_dur)

            # center crop to 9:16
            src_w, src_h = clip.size
            target_ratio = W / H
            src_ratio = src_w / src_h

            if src_ratio > target_ratio:
                # crop width
                new_w = int(src_h * target_ratio)
                x1 = (src_w - new_w) // 2
                clip = crop(clip, x1=x1, y1=0, x2=x1 + new_w, y2=src_h)
            else:
                # crop height
                new_h = int(src_w / target_ratio)
                y1 = (src_h - new_h) // 2
                clip = crop(clip, x1=0, y1=y1, x2=src_w, y2=y1 + new_h)

            clip = clip.resize(newsize=(W, H))

            layers = [clip]
            wmclip = watermark_clip(clip.duration)
            if wmclip is not None:
                layers.append(wmclip)

            final = CompositeVideoClip(layers)
            final.write_videofile(
                str(out_path),
                fps=30,
                codec="libx264",
                audio_codec="aac",
                threads=4,
                preset="medium",
                verbose=False,
                logger=None,
            )
            clip.close()
            final.close()
            created.append(str(out_path))
            msgs.append(f"숏츠 생성(영상 기반): {out_path.name}")

        else:
            # Photo slideshow fallback
            if not photos:
                return PipelineResult(False, ["숏츠 생성 실패: raw 영상도 없고 사진도 없습니다."], [])

            per = max(2.5, min(4.0, max_duration / max(1, min(len(photos), 8))))
            clips = []
            total = 0.0

            for p in photos[:8]:
                img = Image.open(p).convert("RGBA")
                img = _fit_cover(img, W, H)
                img = _apply_watermark(img, wm_img, mode="bottom_center", scale_ratio=0.30)
                # to numpy
                import numpy as np  # type: ignore
                arr = np.array(img)
                c = ImageClip(arr).set_duration(per)
                clips.append(c)
                total += per
                if total >= max_duration:
                    break

            final = concatenate_videoclips(clips, method="compose")
            final.write_videofile(
                str(out_path),
                fps=30,
                codec="libx264",
                audio=False,
                threads=4,
                preset="medium",
                verbose=False,
                logger=None,
            )
            for c in clips:
                c.close()
            final.close()
            created.append(str(out_path))
            msgs.append(f"숏츠 생성(사진 슬라이드): {out_path.name}")

        ok = out_path.exists()
        return PipelineResult(ok, msgs, created)

    except Exception as e:
        msgs.append(f"숏츠 생성 실패: {e}")
        msgs.append(traceback.format_exc()[:2000])
        return PipelineResult(False, msgs, created)


def run_all_generate(paths: PropertyPaths) -> PipelineResult:
    msgs: List[str] = []
    created: List[str] = []

    r1 = process_photos_watermark_and_resize(paths)
    msgs += ["[사진 처리] " + m for m in r1.messages]
    created += r1.created_files

    r2 = render_shorts_video(paths)
    msgs += ["[숏츠 생성] " + m for m in r2.messages]
    created += r2.created_files

    r3 = create_thumbnails(paths)
    msgs += ["[썸네일/카카오] " + m for m in r3.messages]
    created += r3.created_files

    ok = (r1.ok or r2.ok or r3.ok) and any(Path(p).exists() for p in created)
    return PipelineResult(ok, msgs, created)
