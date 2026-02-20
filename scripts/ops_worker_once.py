from __future__ import annotations

import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from services.publish_queue import (
    fetch_due_jobs, mark_running, mark_done, mark_failed
)
from services.youtube_uploader import upload_video_from_payload
from services.config_loader import load_config
from services.meta_ops import read_meta, write_meta, ensure_landing_url

from services.share_payloads import build_kakao_message, write_kakao_payload

def process_job(job):
    print(f"Starting job {job['id']}: {job['channel']} for {job['property_id']} (Priority: {job['priority']})")
    mark_running(job["id"])
    
    try:
        # 1) Execute based on channel
        if job["channel"] == "youtube":
            payload_path = Path(job["payload_path"])
            if not payload_path.exists():
                raise FileNotFoundError(f"Payload not found: {payload_path}")
            
            # Real upload
            res = upload_video_from_payload(payload_path)
            
            # If successful
            url = res.get("watch_url", "")
            print(f"  -> Uploaded! URL: {url}")
            
            # ✅ Meta update
            pid = job["property_id"]
            meta = read_meta(pid)
            meta["uploaded_video_id"] = res.get("video_id")
            meta["uploaded_watch_url"] = url
            meta["published_channel"] = "youtube"
            meta["published_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # 9-6: landing_url 자동 주입
            meta = ensure_landing_url(pid, meta)
            
            write_meta(pid, meta)
            
            # ✅ Kakao payload generation
            landing_url = meta.get("landing_url", "") 
            kakao_payload = build_kakao_message(pid, watch_url=url, landing_url=landing_url)
            write_kakao_payload(pid, kakao_payload)
            print(f"  -> Meta updated & Kakao payload generated.")

        else:
            print(f"Unknown channel: {job['channel']}")
            # For now just mark done if unknown to avoid infinite loop
        
        mark_done(job["id"])
        
    except Exception as e:
        print(f"  -> Failed: {e}")
        mark_failed(job["id"], str(e))

def run_worker_once():
    load_config() # Load secrets
    jobs = fetch_due_jobs(limit=1)
    if not jobs:
        print("No due jobs.")
        return

    for job in jobs:
        process_job(job)

if __name__ == "__main__":
    run_worker_once()
