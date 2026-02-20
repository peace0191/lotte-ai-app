from __future__ import annotations
from pathlib import Path
import os
import sys
import traceback
import tempfile
import shutil

ROOT = Path(__file__).resolve().parent

CHECKS = [
    ("ROOT", ROOT),
    ("app.py", ROOT / "app.py"),
    ("assets/", ROOT / "assets"),
    ("assets/bgm/lounge.mp3", ROOT / "assets" / "bgm" / "lounge.mp3"),
    ("outputs/", ROOT / "outputs"),
    ("outputs/videos/", ROOT / "outputs" / "videos"),
    ("outputs/tts/", ROOT / "outputs" / "tts"),
    ("images/", ROOT / "images"),
]

def can_read(p: Path) -> tuple[bool, str]:
    try:
        if not p.exists():
            return False, "NOT_FOUND"
        if p.is_dir():
            return True, "DIR_OK"
        with p.open("rb") as f:
            f.read(1)
        return True, "FILE_READ_OK"
    except PermissionError:
        return False, "PERMISSION_DENIED"
    except Exception as e:
        return False, f"READ_ERROR: {type(e).__name__}: {e}"

def can_write(dirpath: Path) -> tuple[bool, str]:
    try:
        if not dirpath.exists():
            dirpath.mkdir(parents=True, exist_ok=True)
        test = dirpath / "__write_test__.tmp"
        test.write_text("ok", encoding="utf-8")
        test.unlink(missing_ok=True)
        return True, "WRITE_OK"
    except PermissionError:
        return False, "PERMISSION_DENIED"
    except Exception as e:
        return False, f"WRITE_ERROR: {type(e).__name__}: {e}"

def main():
    print("=== IO / PATH / PERMISSION DIAG ===")
    print("Python:", sys.version)
    print("CWD:", Path.cwd())
    print("ROOT:", ROOT)
    print("TEMP:", Path(tempfile.gettempdir()))
    print()

    # existence + read
    for name, p in CHECKS:
        ok, msg = can_read(p)
        print(f"[READ] {name:<24} -> {str(p)}  => {ok} ({msg})")

    print()
    # write checks (중요: outputs/videos, outputs/tts, ROOT 자체)
    for d in [ROOT, ROOT / "outputs", ROOT / "outputs" / "videos", ROOT / "outputs" / "tts"]:
        ok, msg = can_write(d)
        print(f"[WRITE] {str(d)} => {ok} ({msg})")

    print("\n=== RESULT GUIDE ===")
    print("- NOT_FOUND: 파일/폴더가 없음 (경로/리소스 미존재)")
    print("- PERMISSION_DENIED: 권한 문제 (보안/폴더권한/OneDrive/백신/관리자 권한)")
    print("- WRITE_ERROR: 경로가 잠겼거나(동기화) 디스크/경로 문제 가능")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("\n[FATAL]\n", traceback.format_exc())
