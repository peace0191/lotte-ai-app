from __future__ import annotations
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

# SEOUL = ZoneInfo("Asia/Seoul") 
# ZoneInfo might require python 3.9+ and tzdata. 
# For safety in varied environments, we can fallback or ensure tzdata is present.
# Railway python usually supports it.
try:
    SEOUL = ZoneInfo("Asia/Seoul")
except:
    # Fallback to simple UTC+9 if system doesn't support named zones easily
    from datetime import timezone
    SEOUL = timezone(timedelta(hours=9))

def next_9_or_18_seoul_epoch(now_ts: int | None = None) -> int:
    now = datetime.now(SEOUL) if now_ts is None else datetime.fromtimestamp(now_ts, SEOUL)
    slots = [time(9, 0), time(18, 0)]

    for t in slots:
        candidate = datetime.combine(now.date(), t, tzinfo=SEOUL)
        if candidate > now:
            return int(candidate.timestamp())

    # 오늘 슬롯 다 지났으면 내일 09:00
    tomorrow = now.date() + timedelta(days=1)
    candidate = datetime.combine(tomorrow, time(9, 0), tzinfo=SEOUL)
    return int(candidate.timestamp())
