from typing import List, Dict, Any
from src.config import OMIO_API_KEY

class OmioProvider:
    """Stub for Omio (trains/buses)."""
    def search(self, origin: str, destination: str, date: str) -> List[Dict[str, Any]]:
        if not OMIO_API_KEY:
            return []
        # TODO: implement real API call and normalize results
        return []
