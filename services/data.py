from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

def load_properties() -> Dict[str, List[dict]]:
    try:
        with open(DATA_DIR / "properties.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def load_faq_common() -> dict:
    try:
        with open(DATA_DIR / "faq_common.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
