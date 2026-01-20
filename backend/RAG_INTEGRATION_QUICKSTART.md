# RAG LLM Integration - Quick Start Guide

## Prerequisites

### Verify All Files Created

```bash
# Service layer files
ls -la app/services/rag_prediction_service.py
ls -la app/services/rag_integration.py
ls -la app/services/unified_backend.py

# Endpoint files
ls -la app/api/v1/endpoints/predictions.py
ls -la app/api/v1/endpoints/admin_predictions.py
ls -la app/api/v1/endpoints/dashboard.py

# Configuration
ls -la app/api/v1/api.py
```

### Environment Setup

```bash
# Set required environment variables
export GROQ_API_KEY="your-groq-api-key"
export DATABASE_URL="postgresql://user:pass@localhost/aushadhi"

# Verify RAG service prompt files exist
ls -la rag_llm_service/prompts/system.txt
ls -la rag_llm_service/prompts/quantity_forecast.txt
ls -la rag_llm_service/prompts/constraints.txt
```

## Step 1: Verify Database Schema

Ensure HospitalPrediction table has required columns:

```sql
-- Check if new columns exist (run in PostgreSQL)
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name='hospital_predictions' 
  AND column_name IN ('llm_confidence', 'llm_assumptions', 'llm_risk_flags');
```

**If columns missing**, add them:

```sql
ALTER TABLE hospital_predictions 
ADD COLUMN llm_confidence FLOAT DEFAULT 0.0,
ADD COLUMN llm_assumptions JSONB DEFAULT '[]'::jsonb,
ADD COLUMN llm_risk_flags JSONB DEFAULT '[]'::jsonb;
```

## Step 2: Start Backend Server

```bash
cd c:\robomaneet\projects\aushadhi\backend

# Install dependencies (if needed)
pip install -r requirements.txt
pip install -r rag_llm_service/requirements.txt

# Run server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server should be available at: `http://localhost:8000`

## Step 3: Test Endpoints

### Health Check

```bash
# Check if RAG service is healthy
curl -X GET "http://localhost:8000/admin/predictions/health"
```

Expected Response:
```json
{
  "status": "healthy",
  "rag_service": "active",
  "database": "connected",
  "timestamp": "2024-..."
}
```

### Generate Single Medicine Prediction

```bash
# Get list of hospitals first
curl -X GET "http://localhost:8000/hospitals"

# Get list of medicines
curl -X GET "http://localhost:8000/medicines"

# Generate prediction for specific medicine
curl -X POST "http://localhost:8000/predictions/generate/MED001" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Hospital-ID: HOSP001" \
  -H "Content-Type: application/json"
```

Expected Response:
```json
{
  "success": true,
  "prediction": {
    "hospital_id": "HOSP001",
    "medicine_id": "MED001",
    "medicine_name": "Aspirin",
    "X1_amc": 150.25,
    "X2_prescriptions": 200,
    "safety_stock": 75,
    "reorder_stock": 150,
    "max_stock": 300,
    "llm_confidence": 0.85,
    "llm_assumptions": ["..."],
    "llm_risk_flags": ["..."]
  },
  "database_status": {
    "inserted": 1,
    "updated": 0
  }
}
```

### Generate All Medicines (Async)

```bash
# Start async batch prediction (background task)
curl -X POST "http://localhost:8000/predictions/generate-all" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Hospital-ID: HOSP001" \
  -H "Content-Type: application/json"
```

Expected Response:
```json
{
  "status": "processing",
  "message": "Prediction generation started for all medicines",
  "hospital_id": "HOSP001"
}
```

### Check Prediction Summary

```bash
# Get prediction quality metrics
curl -X GET "http://localhost:8000/admin/predictions/summary/HOSP001" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected Response:
```json
{
  "hospital_id": "HOSP001",
  "total_predictions": 150,
  "average_confidence": 0.82,
  "total_risk_flags": 12,
  "prediction_quality": "high"
}
```

### View Medicine Context

```bash
# See what context was used for prediction
curl -X GET "http://localhost:8000/admin/predictions/medicine/HOSP001/MED001" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected Response:
```json
{
  "medicine_id": "MED001",
  "hospital_id": "HOSP001",
  "context": {
    "medicine": {
      "id": "MED001",
      "name": "Aspirin",
      "unit": "tablet",
      "price": 25.50
    },
    "stock": {
      "current_quantity": 500,
      "expiry_status": "healthy",
      "days_to_expiry": 180
    },
    "usage": {
      "usage_trend": "increasing",
      "avg_consumption": 150.25,
      "days_data": 90
    },
    "recent_orders": [...],
    "active_alerts": [...]
  }
}
```

## Step 4: Monitor Dashboard

```bash
# Get updated dashboard with RAG metrics
curl -X GET "http://localhost:8000/dashboard/hospital/HOSP001" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Dashboard should now show:
- `rag_predictions_total`
- `rag_average_confidence`
- `rag_active_risk_flags`

## Step 5: Run Admin Operations

### Sync Predictions for Hospital

```bash
curl -X POST "http://localhost:8000/admin/predictions/sync/HOSP001" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

### Regenerate Single Prediction

```bash
curl -X POST "http://localhost:8000/admin/predictions/regenerate/HOSP001/MED001" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

### Batch Regenerate All

```bash
curl -X POST "http://localhost:8000/admin/predictions/batch-regenerate/HOSP001" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

### Get Detailed Stats

```bash
curl -X GET "http://localhost:8000/admin/predictions/stats/HOSP001" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected Response:
```json
{
  "hospital_id": "HOSP001",
  "stats": {
    "avg_safety_stock": 75.5,
    "avg_reorder_stock": 150.2,
    "avg_max_stock": 300.1,
    "median_confidence": 0.84,
    "prediction_count": 150,
    "high_confidence_predictions": 130,
    "confidence_distribution": {
      "0.8-0.9": 80,
      "0.7-0.8": 40,
      "0.6-0.7": 20,
      "<0.6": 10
    }
  }
}
```

## Troubleshooting

### Issue: ImportError for RAG service

**Solution:** Ensure RAG service is in Python path:
```bash
export PYTHONPATH="${PYTHONPATH}:./rag_llm_service"
```

### Issue: "GROQ_API_KEY not set"

**Solution:** Set API key before starting server:
```bash
export GROQ_API_KEY="gsk_your_actual_key_here"
```

### Issue: Database connection failed

**Solution:** Verify DATABASE_URL:
```bash
# Test connection
python -c "from sqlalchemy import create_engine; create_engine('$DATABASE_URL').connect()"
```

### Issue: Prompt files not found

**Solution:** Verify prompts exist and server is running from correct directory:
```bash
pwd  # Should be: c:\robomaneet\projects\aushadhi\backend
ls rag_llm_service/prompts/
```

### Issue: RAG service returns 429 (Rate Limited)

**Solution:** Groq API rate limit hit. Wait or check API quota:
```bash
# Check error details
# Response will include retry_after header
```

### Issue: Predictions show low confidence (<0.5)

**Solution:** May indicate missing context or unusual data:
1. Check if hospital has usage data in HospitalUsage table
2. Verify medicine information is complete
3. Check for active alerts affecting predictions

## Testing Workflow

### 1. Single Medicine Test (2 minutes)

```bash
# Start with one medicine to verify everything works
# Generate → Check response → View context → Check stats
curl -X POST "http://localhost:8000/predictions/generate/MED001" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Hospital-ID: HOSP001"
```

### 2. Batch Test (5-10 minutes)

```bash
# Test batch processing with all medicines
curl -X POST "http://localhost:8000/predictions/generate-all" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Hospital-ID: HOSP001"

# Monitor completion (check database)
sqlite3 aushadhi.db "SELECT COUNT(*) FROM hospital_predictions WHERE hospital_id='HOSP001'"
```

### 3. Admin Operations Test (3 minutes)

```bash
# Test all admin endpoints
# Health check → Summary → Stats → Context → Regenerate
```

### 4. Performance Test (10 minutes)

```bash
# Generate predictions for multiple hospitals
# Measure response times and database performance
# Check CPU and memory usage
```

## Integration Verification Checklist

- [ ] Database columns added (llm_confidence, llm_assumptions, llm_risk_flags)
- [ ] All service files created and importable
- [ ] All endpoint files updated
- [ ] API routes registered
- [ ] Environment variables set (GROQ_API_KEY, DATABASE_URL)
- [ ] Prompt files exist in rag_llm_service/prompts/
- [ ] Server starts without errors
- [ ] Health endpoint returns "healthy"
- [ ] Single prediction generates successfully
- [ ] Batch prediction processes in background
- [ ] Admin endpoints accessible with proper auth
- [ ] Dashboard shows RAG metrics
- [ ] Database persistence working (predictions saved)
- [ ] Error handling works for edge cases

## Next Steps

1. **Configure Monitoring**: Set up logs and monitoring for RAG calls
2. **Schedule Batch Jobs**: Set up cron/scheduler for nightly predictions
3. **Load Testing**: Test with production-scale data volumes
4. **User Training**: Explain new confidence scores and risk flags to end users
5. **Feedback Loop**: Collect actual outcomes to improve LLM adjustments

## Useful Commands

```bash
# View recent logs for errors
tail -f logs/app.log | grep -E "ERROR|WARNING"

# Check database statistics
python inspect_db.py

# Test RAG pipeline directly
python -c "from rag_llm_service.pipelines.rag_pipeline import RAGPipeline; p = RAGPipeline(); print(p)"

# Count existing predictions
python -c "from app.database import SessionLocal; from app.models.prediction import HospitalPrediction; db = SessionLocal(); print(db.query(HospitalPrediction).count()); db.close()"

# Check API documentation
# Visit: http://localhost:8000/docs
```

## Support

If you encounter issues:

1. Check logs: `logs/app.log`
2. Enable debug mode: Set `DEBUG=true` in environment
3. Test RAG service directly: See [RAG_INTEGRATION_GUIDE.md](RAG_INTEGRATION_GUIDE.md)
4. Verify database schema: Run schema validation script
5. Check Groq API status: https://status.groq.com/

