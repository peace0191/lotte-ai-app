from __future__ import annotations
from pathlib import Path
import shutil
import random
import os
import sys

def _inject_ffmpeg_env() -> str | None:
    """
    MoviePy/ImageIO가 ffmpeg를 못 찾는 Windows 이슈 방어.
    1) 시스템 PATH의 ffmpeg 우선
    2) 없으면 imageio-ffmpeg의 ffmpeg exe 경로를 찾아 환경변수로 주입
    """
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        # os.environ.setdefault("IMAGEIO_FFMPEG_EXE", sys_ffmpeg) # Optional: Don't override if already set
        return sys_ffmpeg

    try:
        import imageio_ffmpeg  # pip: imageio-ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and Path(exe).exists():
            os.environ["IMAGEIO_FFMPEG_EXE"] = exe
            return exe
    except Exception:
        pass
    return None

def has_ffmpeg() -> bool:
    return _inject_ffmpeg_env() is not None

# --- Compatibility Layer for MoviePy v1 vs v2 ---
# Inject FFmpeg BEFORE importing moviepy
_inject_ffmpeg_env()

_MOVIEPY_IMPORT_ERR = None
try:
    # Try v1 imports first (most common for this codebase)
    from moviepy.editor import (
        ImageClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip,
        TextClip, ColorClip, concatenate_videoclips
    )
    from moviepy.audio.fx.all import audio_fadein, audio_fadeout, volumex
except ImportError as e1:
    try:
        # Try v2 imports (if v1 fails)
        from moviepy import (
            ImageClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip,
            TextClip, ColorClip, concatenate_videoclips
        )
        # Note: audio fx location might differ in v2, simplifying for now
        audio_fadein = audio_fadeout = volumex = None 
    except ImportError as e2:
        # Fallback if moviepy is completely missing
        ImageClip = AudioFileClip = CompositeAudioClip = CompositeVideoClip = TextClip = ColorClip = concatenate_videoclips = None
        audio_fadein = audio_fadeout = volumex = None
        _MOVIEPY_IMPORT_ERR = f"v1 error: {e1}, v2 error: {e2}"
except Exception as e:
     ImageClip = AudioFileClip = CompositeAudioClip = CompositeVideoClip = TextClip = ColorClip = concatenate_videoclips = None
     audio_fadein = audio_fadeout = volumex = None
     _MOVIEPY_IMPORT_ERR = repr(e)

def _require_moviepy():
    if ImageClip is None:
        raise ImportError(f"MoviePy import failed: {_MOVIEPY_IMPORT_ERR}")

def _list_images(images_dir: Path) -> list[Path]:
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    if not images_dir.exists():
        return []
    return sorted([p for p in images_dir.iterdir() if p.suffix.lower() in exts])

def _kb_motion(clip: ImageClip, duration: float, size=(720, 1280)) -> ImageClip:
    """
    Ken Burns: 느린 줌 + 약간의 패닝(가벼운 고급 연출)
    """
    # 기본 체크
    if clip is None: return None

    # 조금 크게 올려두고 천천히 확대
    start_scale = 1.05
    end_scale = 1.12

    # 패닝 방향 랜덤(좌->우 or 우->좌)
    pan_left = random.choice([True, False])

    def resize_at(t):
        return start_scale + (end_scale - start_scale) * (t / duration)

    moving = clip.resize(lambda t: resize_at(t))

    # 패닝: 중앙을 약간 이동
    def pos_at(t):
        w, h = moving.w, moving.h
        # target frame
        fw, fh = size
        # 중심 이동폭(너무 크면 멀미남)
        dx = (w - fw) * 0.10
        x = -dx * (t / duration) if pan_left else -dx * (1 - (t / duration))
        y = 0
        return (x, y)

    return moving.set_position(pos_at)

def _safe_text(txt: str, fontsize: int, size_w: int, duration: float, y: int):
    """
    Windows 폰트/Imagemagick 이슈 최소화: method=caption 고정
    ImageMagick이 없어서 실패하면 None을 반환하여 크래시 방지
    """
    try:
        # Windows에서 ImageMagick이 없거나 폰트 이슈가 있을 때 대비
        # font='Arial' 등 지정할 수도 있으나, moviepy 버전에 따라 다름.
        # 안전하게 기본값 사용
        return TextClip(
            txt=txt,
            fontsize=fontsize,
            color="white",
            method="caption",
            size=(size_w, None),
            align="center"
        ).set_duration(duration).set_position(("center", y))
    except Exception as e:
        print(f"Warning: TextClip failed (ImageMagick missing?): {e}")
        return None

def _build_overlay(title: str, price: str, area: str, tags: list[str], duration: float, size=(720,1280)):
    fw, fh = size
    # 상단 타이틀
    t_title = _safe_text(title, fontsize=46, size_w=660, duration=duration, y=70)

    # 중단 가격/평형(강조)
    t_price = _safe_text(f"{price} | {area}평", fontsize=42, size_w=660, duration=duration, y=190)

    # 하단 태그/CTA 바
    tag_line = "  ".join([f"#{t}" for t in tags[:6]]) if tags else ""
    cta = "문의/방문 예약: 롯데타워앤강남빌딩부동산 (주) 02-578-8285"
    t_tags = _safe_text(tag_line, fontsize=28, size_w=680, duration=duration, y=1040) if tag_line else None
    t_cta  = _safe_text(cta, fontsize=26, size_w=680, duration=duration, y=1110)

    # 반투명 하단 바(CTA 가독성)
    bar = ColorClip(size=(fw, 220), color=(0,0,0)).set_opacity(0.35).set_duration(duration).set_position((0, fh-220))

    layers = [bar]
    
    # 텍스트 클립 생성 성공한 것만 추가
    if t_title: layers.append(t_title)
    if t_price: layers.append(t_price)
    if t_tags: layers.insert(-1, t_tags) # bar 뒤, cta 앞 등 순서 고려 필요하지만 단순 append도 무방
    if t_cta: layers.append(t_cta)
    
    return layers

def _mix_audio(narration_mp3: str | None, bgm_mp3: str | None, video_duration: float,
               bgm_volume=0.12, fade_sec=0.8, ducking=True):
    """
    - narration: 1.0 (기본)
    - bgm: 0.10~0.18 권장
    - fade in/out
    - ducking: 나레이션 있으면 bgm 볼륨을 조금 더 낮춤(간단 덕킹)
    """
    tracks = []
    if narration_mp3 and Path(narration_mp3).exists():
        try:
            nar = AudioFileClip(narration_mp3)
            nar = nar.subclip(0, min(nar.duration, video_duration))
            tracks.append(nar)
        except Exception as e:
            print(f"Warning: Failed to load narration: {e}")

    if bgm_mp3 and Path(bgm_mp3).exists():
        try:
            bgm = AudioFileClip(bgm_mp3)

            # bgm을 영상 길이에 맞게 반복/자르기
            if bgm.duration < video_duration:
                # MoviePy에서 오디오 루프가 복잡하므로, 짧은 BGM이면 그냥 반복없이 자르거나
                # 간단히 이어붙이는 로직 시도 (concatenate_audioclips가 필요하지만 여기선 생략)
                bgm = bgm.subclip(0, min(bgm.duration, video_duration))
            else:
                bgm = bgm.subclip(0, min(bgm.duration, video_duration))

            vol = bgm_volume
            if ducking and narration_mp3:
                vol = min(bgm_volume, 0.10)  # 나레이션 있으면 조금 더 낮게(간단 덕킹)

            if volumex:
                bgm = volumex(bgm, vol)
            elif hasattr(bgm, "volumex"): # v2 style fallback
                bgm = bgm.volumex(vol)
            
            if audio_fadein:
                bgm = audio_fadein(bgm, fade_sec)
            if audio_fadeout:
                bgm = audio_fadeout(bgm, fade_sec)
            tracks.append(bgm)
        except Exception as e:
             print(f"Warning: Failed to load BGM: {e}")

    if not tracks:
        return None
    return CompositeAudioClip(tracks)

def render_premium_shorts(
    *,
    property_id: str,
    title: str,
    price: str,
    area: str,
    tags: list[str],
    images_dir: str,
    narration_mp3: str | None,
    bgm_mp3: str | None,
    out_path: str,
    size=(720, 1280),
    per_image_sec=2.4,
    crossfade=0.35
) -> str:
    """
    ✅ 프리미엄 쇼츠 렌더러:
    - 9:16
    - Ken Burns
    - crossfade
    - 고정 자막 레이아웃 + CTA
    - BGM 레벨링 + 페이드
    """
    if not has_ffmpeg():
         raise RuntimeError("FFmpeg not found (PATH or imageio-ffmpeg).")

    _require_moviepy()

    import tempfile
    
    def _ensure_writable_out(out_path: str) -> Path:
        out = Path(out_path)
        try:
            if not out.parent.exists():
                 out.parent.mkdir(parents=True, exist_ok=True)
            # Test write
            test = out.parent / "__write_test__.tmp"
            test.write_text("ok", encoding="utf-8")
            test.unlink(missing_ok=True)
            return out
        except Exception:
            tmpdir = Path(tempfile.gettempdir()) / "lotte_ai_outputs"
            tmpdir.mkdir(parents=True, exist_ok=True)
            return tmpdir / out.name

    out = _ensure_writable_out(out_path)
    # out.parent.mkdir(parents=True, exist_ok=True) # Already handled in helper

    imgs = _list_images(Path(images_dir))
    clips = []

    if not imgs:
        # 이미지 없으면 브리핑 카드 1개로 대체
        dur = 8
        bg = ColorClip(size=size, color=(10,12,18)).set_duration(dur)
        layers = _build_overlay(title, price, area, tags, dur, size=size)
        v = CompositeVideoClip([bg] + layers, size=size)
        clips = [v]
    else:
        use_imgs = imgs[:8]
        for i, img_path in enumerate(use_imgs):
            try:
                base = ImageClip(str(img_path)).set_duration(per_image_sec)

                # 세로 비율에 맞춰 스케일링(중앙 크롭)
                # v1: resize(height=...)
                base = base.resize(height=size[1])
                if base.w > size[0]:
                    x1 = (base.w - size[0]) / 2
                    base = base.crop(x1=x1, y1=0, x2=x1+size[0], y2=size[1])
                else:
                    base = base.on_color(size=size, color=(0,0,0), pos=("center","center"))

                # Ken Burns motion
                motion = _kb_motion(base, per_image_sec, size=size)

                # Overlay
                layers = _build_overlay(title, price, area, tags, per_image_sec, size=size)
                clip = CompositeVideoClip([motion] + layers, size=size)

                # crossfade(첫 장 제외)
                if i > 0:
                    clip = clip.crossfadein(crossfade)

                clips.append(clip)
            except Exception as e:
                print(f"Skipping bad image {img_path}: {e}")
                continue

        if not clips:
             raise RuntimeError("No valid images found or all images failed to load.")
             
        final = concatenate_videoclips(clips, method="compose")
        
        # Audio
        audio = _mix_audio(narration_mp3, bgm_mp3, final.duration, bgm_volume=0.12, fade_sec=0.8, ducking=True)
        if audio:
            final = final.set_audio(audio)

        # Write file
        # temp_audiofile helps avoid permission issues on Windows sometimes
        final.write_videofile(
            str(out), 
            fps=24, 
            codec="libx264", 
            audio=bool(audio),
            audio_codec="aac",
            temp_audiofile=f"temp-audio-{property_id}.m4a",
            remove_temp=True,
            threads=4
        )

    # 이미지 없었던 브리핑 카드 케이스도 오디오 적용 (위에서 이미 clips[0]에 audio 적용 안 했으므로)
    if not imgs:
        v = clips[0]
        audio = _mix_audio(narration_mp3, bgm_mp3, v.duration, bgm_volume=0.12, fade_sec=0.8, ducking=True)
        if audio:
            v = v.set_audio(audio)
        v.write_videofile(
            str(out), 
            fps=24, 
            codec="libx264", 
            audio=bool(audio),
            audio_codec="aac",
            temp_audiofile=f"temp-audio-{property_id}.m4a",
            remove_temp=True
        )
    
    return str(out)

