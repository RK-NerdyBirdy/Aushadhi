# Aushadhi – LLM RAG Service

This service provides an LLM-based Retrieval-Augmented Generation (RAG) pipeline
for forecasting hospital medicine procurement quantities.

## Tech Stack
- Neon PostgreSQL (structured data source)
- Groq LLMs (numeric reasoning)
- FastAPI (API layer)
- RAG (contextual retrieval, no ML overlap)

## Responsibilities
- Retrieve structured hospital inventory data
- Convert it into LLM-friendly context
- Predict required medicine quantities using LLM reasoning
- Expose APIs for downstream ML reconciliation

## Run Locally

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
