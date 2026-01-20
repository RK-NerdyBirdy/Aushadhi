from rag_llm_service.retrieval.context_builder import ContextBuilder
from rag_llm_service.retrieval.embedding_store import EmbeddingStore
from sentence_transformers import SentenceTransformer

def main():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    store = EmbeddingStore()
    builder = ContextBuilder()

    hospitals = ["HOSP001"]

    for hospital_id in hospitals:
        medicine_ids = []  # populate dynamically later

        for mid in medicine_ids:
            context = builder.build_context(hospital_id, mid)
            embedding = model.encode(context)
            store.add(embedding, context)

    print("Embeddings built successfully")

if __name__ == "__main__":
    main()
