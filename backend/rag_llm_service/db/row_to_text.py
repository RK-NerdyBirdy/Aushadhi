"""
This module provides functions to format database rows into text for the LLM context.
"""

def format_rows_to_text(title: str, rows: list[dict]) -> str:
    """
    Formats a list of database rows into a string block.
    """
    if not rows:
        return ""
    
    block = f"--- {title} ---\n"
    for row in rows:
        for key, value in row.items():
            block += f"{key.replace('_', ' ').title()}: {value}\n"
        block += "\n"
    return block.strip() + "\n\n"

def build_context_block(
    usage_summary: list[dict],
    stock_levels: list[dict],
    prediction_inputs: list[dict],
    medicine_info: list[dict],
    recent_orders: list[dict]
) -> str:
    """
    Builds a complete context block from various data sources.
    """
    context = ""
    context += format_rows_to_text("Usage Summary", usage_summary)
    context += format_rows_to_text("Current Stock Levels", stock_levels)
    context += format_rows_to_text("Prediction Inputs", prediction_inputs)
    context += format_rows_to_text("Medicine Information", medicine_info)
    context += format_rows_to_text("Recent Orders", recent_orders)
    
    return context.strip()

