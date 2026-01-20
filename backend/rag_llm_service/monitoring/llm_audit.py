from datetime import datetime

def audit_llm_call(
    hospital_id,
    medicine_id,
    context,
    llm_output,
    model_name
):
    return {
        "hospital_id": hospital_id,
        "medicine_id": medicine_id,
        "model": model_name,
        "context_snapshot": context,
        "llm_output": llm_output,
        "timestamp": datetime.utcnow().isoformat()
    }
