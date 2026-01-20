from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database import Base, engine
from app.api.endpoints import auth, upload, predictions, procurement, dashboard, alerts

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Hospital Drug Inventory Management System",
    description="AI-powered drug inventory optimization using demand prediction and clustering",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(predictions.router)
app.include_router(procurement.router)
app.include_router(dashboard.router)
app.include_router(alerts.router)


@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "Hospital Drug Inventory Management System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Hospital Drug Inventory API"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
