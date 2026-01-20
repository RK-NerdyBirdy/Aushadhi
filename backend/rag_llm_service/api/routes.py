from fastapi import APIRouter
from api.schemas import QuantityRequest, BatchQuantityRequest
from pipelines.rag_pipeline import RAGPipeline
from pipelines.batch_pipeline import BatchPipeline

router = APIRouter()

# Load prompts at module level (VALID Python)
with open("prompts/system.txt", "r") as f:
    SYSTEM_PROMPT = f.read()

with open("prompts/quantity_forecast.txt", "r") as f:
    FORECAST_PROMPT = f.read()

with open("prompts/constraints.txt", "r") as f:
    CONSTRAINTS_PROMPT = f.read()

rag_pipeline = RAGPipeline(
    SYSTEM_PROMPT,
    FORECAST_PROMPT,
    CONSTRAINTS_PROMPT
)

batch_pipeline = BatchPipeline(rag_pipeline)


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/rag/predict-quantity")
def predict_quantity(req: QuantityRequest):
    return rag_pipeline.run(
        req.hospital_id,
        req.medicine_id,
        req.forecast_days
    ).dict()



@router.post("/rag/batch-predict")
def batch_predict(req: BatchQuantityRequest):
    return {
        "results": batch_pipeline.run(
            req.hospital_id,
            req.medicine_ids,
            req.forecast_days
        )
    }
