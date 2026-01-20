from fastapi import FastAPI
from rag_llm_service.api.routes import router

app = FastAPI(
    title="Aushadhi RAG LLM Service",
    version="1.0.0"
)
app = FastAPI()
app.include_router(router)
