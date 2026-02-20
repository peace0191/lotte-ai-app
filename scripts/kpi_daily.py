"""
scripts/kpi_daily.py
====================
systemd daily 타이머에서 호출되는 KPI 생성 스크립트.
매일 23:55에 자동 실행됩니다.

직접 실행:
    python scripts/kpi_daily.py
    python scripts/kpi_daily.py --yesterday    # 전날 리포트 재생성
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

# ── 프로젝트 루트를 sys.path에 추가 ──────────────────────
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from services.kpi_report import write_daily_csv
except ImportError:
    print("Error: services.kpi_report not found. Make sure you run this script from project root or add root to pythonpath.", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    # 인수 파싱: --yesterday 옵션 지원
    yesterday_mode = "--yesterday" in sys.argv

    target = datetime.now()
    if yesterday_mode:
        target = target - timedelta(days=1)
        print(f"[kpi_daily] 모드: 전날 리포트 ({target.strftime('%Y-%m-%d')})")
    else:
        print(f"[kpi_daily] 모드: 오늘 리포트 ({target.strftime('%Y-%m-%d')})")

    try:
        path = write_daily_csv(target)
        print(f"[kpi_daily] 생성 완료: {path.as_posix()}")
        sys.exit(0)
    except Exception as e:
        print(f"[kpi_daily] 오류: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
