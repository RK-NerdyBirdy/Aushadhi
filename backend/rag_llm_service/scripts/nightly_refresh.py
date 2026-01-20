from pipelines.batch_pipeline import BatchPipeline
from pipelines.rag_pipeline import RAGPipeline

with open("prompts/system.txt") as f:
    SYSTEM_PROMPT = f.read()

with open("prompts/quantity_forecast.txt") as f:
    FORECAST_PROMPT = f.read()

with open("prompts/constraints.txt") as f:
    CONSTRAINTS_PROMPT = f.read()

def main():
    rag = RAGPipeline(
        SYSTEM_PROMPT,
        FORECAST_PROMPT,
        CONSTRAINTS_PROMPT
    )

    batch = BatchPipeline(rag)

    hospital_id = "HOSP001"
    medicine_ids = []  # populate dynamically later

    results = batch.run(hospital_id, medicine_ids)
    print("Nightly refresh completed")

if __name__ == "__main__":
    main()
