from datetime import datetime
from typing import List

def parse_expiry_warning_days() -> List[int]:
    """Parse EXPIRY_WARNING_DAYS from environment"""
    from app.core.config import settings
    days_str = settings.EXPIRY_WARNING_DAYS
    return [int(d.strip()) for d in days_str.split(',')]

def get_current_timestamp() -> datetime:
    """Get current timestamp"""
    return datetime.utcnow()
