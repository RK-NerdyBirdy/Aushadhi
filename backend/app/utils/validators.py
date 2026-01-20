import re


def validate_csv_stock_format(required_columns: set, file_columns: set) -> tuple[bool, str]:
    """Validate stock CSV has required columns"""
    missing = required_columns - file_columns
    if missing:
        return False, f"Missing columns: {', '.join(missing)}"
    return True, ""


def validate_csv_usage_format(required_columns: set, file_columns: set) -> tuple[bool, str]:
    """Validate usage CSV has required columns"""
    missing = required_columns - file_columns
    if missing:
        return False, f"Missing columns: {', '.join(missing)}"
    return True, ""


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_positive_integer(value: int) -> bool:
    """Validate value is a positive integer"""
    return isinstance(value, int) and value >= 0


def validate_positive_float(value: float) -> bool:
    """Validate value is a positive float"""
    return isinstance(value, (int, float)) and value >= 0
