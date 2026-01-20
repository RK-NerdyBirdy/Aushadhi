# RAG LLM Service Integration Documentation

## Overview

The backend has been unified to integrate the RAG LLM Service with the core hospital inventory management system. This provides AI-powered, context-aware medicine predictions instead of traditional K-Means clustering.

## Architecture

### Service Layers

```
┌─────────────────────────────────────┐
│      FastAPI Endpoints Layer        │
├─────────────────────────────────────┤
│  predictions.py | admin_predictions │
├─────────────────────────────────────┤
│   Unified Backend Service Layer      │
│  (unified_backend.py)               │
├─────────────────────────────────────┤
│   RAG Integration Layer              │
│  (rag_integration.py)               │
├─────────────────────────────────────┤
│   RAG LLM Service                    │
│  (rag_prediction_service.py)        │
├─────────────────────────────────────┤
│   RAG Pipeline                       │
│  (rag_llm_service/pipelines/)       │
├─────────────────────────────────────┤
│   Database Layer                     │
│  (SQLAlchemy Models & CRUD)         │
└─────────────────────────────────────┘
```

## Key Components

### 1. RAG Prediction Service (`app/services/rag_prediction_service.py`)

**Purpose:** Core service that generates LLM-enhanced predictions for medicines

**Key Methods:**
- `generate_predictions_for_medicine()` - Generate single medicine prediction
- `generate_all_predictions_for_hospital()` - Batch process all medicines
- `save_predictions_to_db()` - Persist predictions to database

**Features:**
- Loads prompts from `rag_llm_service/prompts/`
- Integrates with RAG pipeline for context-aware adjustments
- Calculates baseline metrics from usage data
- Applies LLM-suggested adjustment factors

### 2. RAG Integration Module (`app/services/rag_integration.py`)

**Components:**

#### RAGContextBuilder
- Builds comprehensive context for each medicine
- Fetches: medicine info, current stock, usage patterns, orders, alerts
- Analyzes: expiry status, usage trends, active risk factors
- Returns structured context JSON for RAG pipeline

#### RAGResultProcessor
- Formats RAG output into app-compatible schema
- Extracts prediction metrics from LLM adjustments
- Maps RAG results to database field names

#### RAGServiceIntegration
- Orchestrates hospital-wide predictions
- Processes prediction batches with contexts

### 3. Unified Backend Service (`app/services/unified_backend.py`)

**Main Interface:** Single entry point for all prediction operations

**Key Methods:**
- `predict_medicine_requirements()` - Single prediction with full context
- `predict_all_medicines()` - Hospital-wide predictions
- `get_hospital_prediction_summary()` - Quality metrics and statistics
- `sync_all_predictions()` - Full synchronization with database

**Features:**
- Unified error handling
- Context inclusion control
- Automatic database persistence
- Quality metrics tracking

## API Endpoints

### Prediction Endpoints

#### `POST /predictions/generate/{medicine_id}`
Generate prediction for specific medicine using RAG LLM

```json
Request: None
Response: {
  "success": true,
  "prediction": {
    "hospital_id": "HOSP001",
    "medicine_id": "MED001",
    "X1_amc": 150.25,
    "X2_prescriptions": 200,
    "safety_stock": 75,
    "reorder_stock": 150,
    "max_stock": 300,
    "llm_confidence": 0.85,
    "llm_assumptions": [...],
    "llm_risk_flags": [...]
  },
  "database_status": {"inserted": 1, "updated": 0}
}
```

#### `POST /predictions/generate-all`
Generate predictions for all medicines (async background task)

```json
Response: {
  "status": "processing",
  "message": "Prediction generation started for all medicines",
  "hospital_id": "HOSP001"
}
```

#### `POST /predictions/sync`
Sync all predictions from RAG service (async)

```json
Request: {
  "hospital_id": "HOSP001"
}
Response: {
  "message": "Prediction sync initiated for hospital",
  "hospital_id": "HOSP001",
  "service": "RAG_LLM_Pipeline"
}
```

### Admin Management Endpoints

#### `POST /admin/predictions/sync/{hospital_id}`
Admin endpoint to sync predictions for hospital

#### `GET /admin/predictions/summary/{hospital_id}`
Get prediction quality metrics and statistics

```json
Response: {
  "hospital_id": "HOSP001",
  "total_predictions": 150,
  "average_confidence": 0.82,
  "total_risk_flags": 12,
  "prediction_quality": "high"
}
```

#### `GET /admin/predictions/medicine/{hospital_id}/{medicine_id}`
Get complete context used for medicine prediction

```json
Response: {
  "medicine_id": "MED001",
  "hospital_id": "HOSP001",
  "context": {
    "medicine": {...},
    "stock": {...},
    "usage": {...},
    "recent_orders": [...],
    "active_alerts": [...]
  }
}
```

#### `POST /admin/predictions/regenerate/{hospital_id}/{medicine_id}`
Force regenerate prediction for specific medicine

#### `POST /admin/predictions/batch-regenerate/{hospital_id}`
Batch regenerate all predictions (background task)

#### `GET /admin/predictions/health`
Check RAG service health status

#### `GET /admin/predictions/stats/{hospital_id}`
Get detailed prediction statistics

## Data Flow

### Single Medicine Prediction Flow

```
1. Request: /predictions/generate/{medicine_id}
   ↓
2. RAGContextBuilder.build_medicine_context()
   - Fetch medicine info, stock, usage, orders, alerts
   - Analyze trends and expiry status
   ↓
3. RAG Pipeline executes:
   - Build baseline metrics from usage
   - Create context string
   - Call Groq LLM with prompts
   - Get adjustment factor & confidence
   ↓
4. RAGPredictionService.apply_llm_adjustments()
   - Apply LLM adjustment_factor to baseline
   - Calculate safety stock, reorder point, max stock
   ↓
5. Save to database (upsert pattern)
   ↓
6. Return formatted prediction with context
```

### Hospital-Wide Prediction Flow

```
1. Request: /predictions/generate-all (async)
   ↓
2. Iterate all medicines in hospital
   ↓
3. For each medicine:
   - Single prediction flow (see above)
   - Collect results and errors
   ↓
4. Batch save to database
   ↓
5. Return summary with success/failure counts
```

## Database Schema Integration

### HospitalPrediction Model

```python
class HospitalPrediction(Base):
    hospital_id          # FK to organizations
    medicine_id          # FK to medicine_info
    medicine_name
    X1_amc               # Average monthly consumption
    X2_prescriptions     # Prescription count
    X3_CDPR              # Chronic disease prevalence
    X4_CV                # Coefficient of variation
    lead_time
    safety_stock
    reorder_stock
    max_stock
    daily_holding_charges
    llm_confidence       # LLM-provided confidence score
    llm_assumptions      # Assumptions made by LLM
    llm_risk_flags       # Risk factors identified by LLM
```

## Configuration

### Environment Variables Required

```bash
# RAG Service (already in rag_llm_service)
GROQ_API_KEY=your-key
DATABASE_URL=postgresql://...
```

### Prompt Files

Located in `rag_llm_service/prompts/`:
- `system.txt` - System prompt for LLM
- `quantity_forecast.txt` - Forecast generation prompt
- `constraints.txt` - Constraints and guidelines

## Integration Points

### With Existing Services

1. **Prediction Endpoints** - Enhanced with RAG output
2. **Dashboard** - Shows RAG confidence metrics
3. **Stock Management** - Uses RAG-predicted reorder points
4. **Orders** - Based on RAG predictions
5. **Alerts** - Risk flags from LLM

### Data Dependencies

- **Medicine Info** - Price, storage requirements, composition
- **Stock Data** - Current quantities, expiry dates
- **Usage History** - 90-day consumption patterns
- **Orders** - Recent order patterns
- **Alerts** - Active issues affecting predictions

## Performance Considerations

### Single Medicine Prediction
- Time: ~2-3 seconds (including LLM call)
- DB Queries: 5 (medicine, stock, usage, orders, alerts)

### Hospital-Wide Prediction
- Time: Background task (batch processing)
- Recommended: Run nightly or weekly
- Scales linearly with medicine count

### Optimization Tips

1. **Batch Operations**: Use `/generate-all` instead of individual calls
2. **Caching**: Context is reused within batch operations
3. **Background Tasks**: Use async endpoints for large operations
4. **Database Indexes**: Ensure indexes on hospital_id, medicine_id

## Error Handling

### Common Errors

1. **Medicine Not Found**
   - Check medicine exists in medicine_info
   - Verify hospital_id matches

2. **No Usage Data**
   - Predictions use defaults if no usage history
   - Upload usage data via CSV for better predictions

3. **RAG Service Timeout**
   - Check Groq API connectivity
   - Verify GROQ_API_KEY is set
   - Check DATABASE_URL connection

### Error Response Format

```json
{
  "success": false,
  "error": "Error message",
  "context": {...} // if available
}
```

## Monitoring

### Health Checks

```bash
GET /admin/predictions/health
```

### Prediction Quality Metrics

```bash
GET /admin/predictions/summary/{hospital_id}
# Returns: total_predictions, average_confidence, risk_flags, quality_score
```

### Detailed Statistics

```bash
GET /admin/predictions/stats/{hospital_id}
# Returns: average safety stock, reorder stock, max stock
```

## Usage Examples

### Generate Single Prediction

```python
from app.services.unified_backend import unified_backend
from app.database import SessionLocal

db = SessionLocal()
result = unified_backend.predict_medicine_requirements(
    hospital_id="HOSP001",
    medicine_id="MED001",
    db=db,
    include_context=True
)
db.close()
```

### Generate All Predictions

```python
result = unified_backend.predict_all_medicines(
    hospital_id="HOSP001",
    db=db,
    save_to_db=True
)

print(f"Success: {result['success']}")
print(f"Successful: {result['successful_predictions']}")
print(f"Failed: {result['failed_predictions']}")
```

### Get Prediction Summary

```python
summary = unified_backend.get_hospital_prediction_summary(
    hospital_id="HOSP001",
    db=db
)

print(f"Total predictions: {summary['total_predictions']}")
print(f"Average confidence: {summary['average_confidence']}")
print(f"Quality: {summary['prediction_quality']}")
```

## Future Enhancements

1. **Prediction Versioning** - Track prediction history
2. **Feedback Loop** - Improve predictions based on actual outcomes
3. **Seasonal Adjustments** - Factor in seasonal patterns
4. **Multi-Hospital Analytics** - Cross-hospital insights
5. **Real-time Adjustments** - Update predictions as data arrives
6. **Custom LLM Models** - Support for different LLM providers

## Support & Debugging

### Enable Detailed Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test RAG Service Locally

```python
from rag_llm_service.pipelines.rag_pipeline import RAGPipeline

pipeline = RAGPipeline(
    system_prompt="...",
    forecast_prompt="...",
    constraints_prompt="..."
)
result = pipeline.run(hospital_id="HOSP001", medicine_id="MED001")
```

### Verify Database Connection

```python
from rag_llm_service.db.neon_client import NeonClient

client = NeonClient()
result = client.fetch_one("SELECT 1")  # Simple connectivity test
```
