import json
from pathlib import Path
from typing import Optional, Dict, Any

DB_PATH = Path(__file__).parent / "baggage_policies.json"

def get_baggage_policy(carrier_name: str) -> Optional[Dict[str, Any]]:
    if not DB_PATH.exists():
        return None
    data = json.loads(DB_PATH.read_text(encoding="utf-8"))
    return data.get(carrier_name)
