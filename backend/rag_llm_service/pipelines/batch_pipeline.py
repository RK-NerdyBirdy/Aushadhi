from pipelines.rag_pipeline import RAGPipeline

class BatchPipeline:
    def __init__(self, rag_pipeline):
        self.rag = rag_pipeline

    def run(self, hospital_id, medicine_ids):
        results = []

        for mid in medicine_ids:
            try:
                result = self.rag.run(hospital_id, mid)
                results.append(result.dict())
            except Exception as e:
                results.append({
                    "hospital_id": hospital_id,
                    "medicine_id": mid,
                    "error": str(e)
                })

        return results
