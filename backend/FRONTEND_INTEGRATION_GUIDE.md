# Frontend Integration Guide - RAG LLM Backend

## Overview

The frontend integrates with a FastAPI backend that provides LLM-enhanced medicine prediction capabilities. The backend generates AI-powered inventory predictions using Groq's LLM service with real-time context from the hospital database.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React/Vue/etc)                 │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Dashboard    │  │ Predictions  │  │ Admin Panel      │  │
│  │ Component    │  │ Component    │  │ Component        │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                   │            │
│         └─────────────────┼───────────────────┘            │
│                           │                                 │
└───────────────────────────┼─────────────────────────────────┘
                            │
                    HTTP/REST API
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼────────┐
│ Predictions    │  │ Admin       │  │ Dashboard       │
│ Endpoints      │  │ Endpoints   │  │ Endpoints       │
└────────┬───────┘  └──────┬──────┘  └────────┬────────┘
         │                 │                  │
         └─────────────────┼──────────────────┘
                           │
              ┌────────────▼────────────┐
              │   Unified Backend       │
              │   Service Layer         │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │  RAG LLM Pipeline       │
              │  (Groq + Context)       │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │   PostgreSQL Database   │
              └────────────────────────┘
```

---

## Authentication

### Bearer Token Authentication

All API requests require an `Authorization` header with a Bearer token:

```javascript
const headers = {
  "Authorization": `Bearer ${accessToken}`,
  "Content-Type": "application/json"
};
```

### Token Flow

1. User logs in via `/auth/login` endpoint
2. Backend returns `access_token` and `refresh_token`
3. Frontend stores token in secure storage (localStorage/sessionStorage)
4. Include token in all subsequent requests
5. Handle 401 responses by refreshing token or redirecting to login

```javascript
// Example with axios interceptor
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

## Core API Endpoints

### 1. Generate Single Medicine Prediction

**Endpoint:** `POST /predictions/generate/{medicine_id}`

**Headers:**
```
Authorization: Bearer {token}
X-Hospital-ID: HOSP001
Content-Type: application/json
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "hospital_id": "HOSP001",
    "medicine_id": "MED001",
    "medicine_name": "Aspirin",
    "x1_amc": 150.25,
    "x2_prescriptions": 200,
    "x3_cdpr": 0.15,
    "x4_cv": 0.25,
    "lead_time": 7,
    "safety_stock": 75,
    "reorder_stock": 150,
    "max_stock": 300,
    "daily_holding_charges": 2.50,
    "llm_confidence": 0.85,
    "llm_assumptions": [
      "Based on 90-day usage average",
      "Accounts for seasonal trend (stable)",
      "No critical alerts detected"
    ],
    "llm_risk_flags": [
      "Stock expiry in 30 days - recommend usage promotion"
    ]
  },
  "database_status": {
    "inserted": 1,
    "updated": 0
  }
}
```

**Frontend Usage:**
```javascript
async function generatePrediction(medicineId) {
  try {
    const response = await fetch(
      `/predictions/generate/${medicineId}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Hospital-ID': hospitalId,
          'Content-Type': 'application/json'
        }
      }
    );
    
    const data = await response.json();
    if (data.success) {
      // Update UI with prediction
      displayPrediction(data.prediction);
    }
  } catch (error) {
    console.error('Prediction generation failed:', error);
  }
}
```

---

### 2. Generate All Medicines (Background Task)

**Endpoint:** `POST /predictions/generate-all`

**Headers:**
```
Authorization: Bearer {token}
X-Hospital-ID: HOSP001
Content-Type: application/json
```

**Response (Immediate):**
```json
{
  "status": "processing",
  "message": "Prediction generation started for all medicines",
  "hospital_id": "HOSP001"
}
```

**Background Task Completion:**
- Task runs asynchronously
- Frontend should poll `/admin/predictions/summary/{hospital_id}` to check progress
- Or implement WebSocket for real-time updates

**Frontend Usage:**
```javascript
async function generateAllPredictions() {
  // Start background task
  const response = await fetch('/predictions/generate-all', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'X-Hospital-ID': hospitalId
    }
  });
  
  // Poll for completion
  const pollInterval = setInterval(async () => {
    const summary = await getPredictionSummary();
    if (summary.total_predictions > 0) {
      clearInterval(pollInterval);
      showSuccessNotification('All predictions generated');
    }
  }, 5000); // Poll every 5 seconds
}
```

---

### 3. Get Prediction Summary

**Endpoint:** `GET /admin/predictions/summary/{hospital_id}`

**Headers:**
```
Authorization: Bearer {adminToken}
```

**Response:**
```json
{
  "hospital_id": "HOSP001",
  "total_predictions": 150,
  "average_confidence": 0.82,
  "total_risk_flags": 12,
  "prediction_quality": "high"
}
```

**Quality Levels:**
- `high` - average_confidence > 0.80
- `medium` - average_confidence 0.60-0.80
- `low` - average_confidence < 0.60

**Frontend Usage:**
```javascript
async function fetchPredictionSummary() {
  const response = await fetch(
    `/admin/predictions/summary/${hospitalId}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  const summary = await response.json();
  updateDashboard({
    totalPredictions: summary.total_predictions,
    avgConfidence: (summary.average_confidence * 100).toFixed(1),
    qualityScore: summary.prediction_quality
  });
}
```

---

### 4. Get Medicine Context

**Endpoint:** `GET /admin/predictions/medicine/{hospital_id}/{medicine_id}`

**Headers:**
```
Authorization: Bearer {adminToken}
```

**Response:**
```json
{
  "medicine_id": "MED001",
  "hospital_id": "HOSP001",
  "context": {
    "medicine": {
      "id": "MED001",
      "name": "Aspirin",
      "unit": "tablet",
      "price": 25.50,
      "manufacturer": "ABC Pharma"
    },
    "stock": {
      "current_quantity": 500,
      "expiry_status": "healthy",
      "days_to_expiry": 180,
      "storage_location": "Shelf A1"
    },
    "usage": {
      "usage_trend": "increasing",
      "avg_consumption": 150.25,
      "days_data": 90,
      "peak_usage_month": "December"
    },
    "recent_orders": [
      {
        "order_id": 1001,
        "quantity": 500,
        "status": "delivered",
        "delivery_date": "2024-12-15"
      }
    ],
    "active_alerts": [
      {
        "type": "expiry_warning",
        "message": "Stock expires in 30 days"
      }
    ]
  }
}
```

**Frontend Usage:**
```javascript
async function showPredictionContext(medicineId) {
  const response = await fetch(
    `/admin/predictions/medicine/${hospitalId}/${medicineId}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  
  const data = await response.json();
  displayContextModal({
    medicine: data.context.medicine,
    stock: data.context.stock,
    usage: data.context.usage,
    orders: data.context.recent_orders,
    alerts: data.context.active_alerts
  });
}
```

---

### 5. Get Prediction Statistics

**Endpoint:** `GET /admin/predictions/stats/{hospital_id}`

**Headers:**
```
Authorization: Bearer {adminToken}
```

**Response:**
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

---

### 6. Health Check

**Endpoint:** `GET /admin/predictions/health`

**Response:**
```json
{
  "status": "healthy",
  "rag_service": "active",
  "database": "connected",
  "timestamp": "2024-01-21T10:30:00Z"
}
```

**Frontend Usage:**
```javascript
// Check service health periodically
setInterval(async () => {
  try {
    const response = await fetch('/admin/predictions/health');
    const data = await response.json();
    updateServiceStatus(data.status === 'healthy');
  } catch (error) {
    updateServiceStatus(false);
  }
}, 30000); // Check every 30 seconds
```

---

## Request/Response Patterns

### Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": "Medicine not found",
  "error_code": "MEDICINE_NOT_FOUND",
  "details": {
    "medicine_id": "MED999",
    "hospital_id": "HOSP001"
  }
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `500` - Server Error

**Frontend Error Handling:**
```javascript
async function apiCall(endpoint, options = {}) {
  try {
    const response = await fetch(endpoint, options);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'API request failed');
    }
    
    return data;
  } catch (error) {
    if (error.response?.status === 401) {
      // Refresh token or redirect to login
      redirectToLogin();
    } else {
      showErrorNotification(error.message);
    }
    throw error;
  }
}
```

---

## UI Components Architecture

### 1. Dashboard Component

**Displays:**
- Total predictions count
- Average confidence score (visual gauge)
- Risk flags overview
- Recent prediction activity

```javascript
function PredictionDashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchSummary();
    const interval = setInterval(fetchSummary, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="dashboard">
      <ConfidenceGauge value={summary?.average_confidence} />
      <PredictionStats summary={summary} />
      <RiskFlagsPanel flags={summary?.total_risk_flags} />
    </div>
  );
}
```

### 2. Predictions List Component

**Displays:**
- All medicines with predictions
- Prediction metrics (AMC, safety stock, reorder point)
- Confidence score with color coding
- Action buttons (view details, regenerate)

```javascript
function PredictionsList() {
  const [predictions, setPredictions] = useState([]);
  
  return (
    <table>
      <thead>
        <tr>
          <th>Medicine</th>
          <th>AMC</th>
          <th>Safety Stock</th>
          <th>Reorder Point</th>
          <th>Confidence</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {predictions.map(pred => (
          <PredictionRow key={pred.medicine_id} prediction={pred} />
        ))}
      </tbody>
    </table>
  );
}
```

### 3. Prediction Details Modal

**Displays:**
- Full prediction data
- LLM assumptions and reasoning
- Risk flags with explanations
- Context data (usage trends, stock levels, alerts)
- Action buttons (update, regenerate)

```javascript
function PredictionDetailsModal({ medicineId, onClose }) {
  const [context, setContext] = useState(null);
  
  useEffect(() => {
    fetchPredictionContext(medicineId);
  }, [medicineId]);
  
  return (
    <Modal>
      <MedicineInfo data={context?.medicine} />
      <StockStatus data={context?.stock} />
      <UsageTrends data={context?.usage} />
      <LLMAssumptions assumptions={context?.llm_assumptions} />
      <RiskFlags flags={context?.llm_risk_flags} />
      <RecentOrders orders={context?.recent_orders} />
    </Modal>
  );
}
```

### 4. Batch Operations Component

**Displays:**
- Generate all predictions button
- Progress indicator
- Task status updates
- Completion summary

```javascript
function BatchOperations() {
  const [status, setStatus] = useState(null);
  const [progress, setProgress] = useState(0);
  
  const handleGenerateAll = async () => {
    await startBatchGeneration();
    
    // Poll for status
    const pollInterval = setInterval(async () => {
      const summary = await getPredictionSummary();
      setProgress(summary.total_predictions);
      
      if (summary.total_predictions >= expectedCount) {
        setStatus('completed');
        clearInterval(pollInterval);
      }
    }, 5000);
  };
  
  return (
    <div className="batch-operations">
      <button onClick={handleGenerateAll}>Generate All Predictions</button>
      {status && <ProgressBar value={progress} />}
      {status === 'completed' && <SuccessMessage />}
    </div>
  );
}
```

---

## State Management Considerations

### Redux/Vuex Store Structure

```javascript
// Predictions State
{
  predictions: {
    byId: {
      'MED001': { ...predictionData },
      'MED002': { ...predictionData }
    },
    allIds: ['MED001', 'MED002'],
    summary: {
      total: 150,
      avgConfidence: 0.82,
      qualityScore: 'high'
    },
    loading: false,
    error: null,
    lastUpdate: '2024-01-21T10:30:00Z'
  },
  admin: {
    selectedHospital: 'HOSP001',
    batchOperations: {
      inProgress: false,
      totalCount: 150,
      completedCount: 75
    }
  }
}
```

### Actions/Mutations

```javascript
// Redux Actions
export const predictionsSlice = createSlice({
  name: 'predictions',
  initialState,
  reducers: {
    setPredictions: (state, action) => {
      // Update predictions
    },
    updateSummary: (state, action) => {
      // Update summary stats
    },
    setBatchProgress: (state, action) => {
      // Update batch operation progress
    }
  }
});
```

---

## Real-Time Updates Strategy

### Option 1: Polling (Recommended for MVP)

```javascript
// Poll every 10 seconds
setInterval(async () => {
  const summary = await fetch(`/admin/predictions/summary/${hospitalId}`);
  dispatch(updateSummary(await summary.json()));
}, 10000);
```

### Option 2: WebSocket (Future Enhancement)

```javascript
const ws = new WebSocket('ws://backend/predictions/stream');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  if (update.type === 'prediction_generated') {
    dispatch(addPrediction(update.data));
  }
};
```

---

## Error Handling & Retry Logic

```javascript
async function apiCallWithRetry(
  endpoint,
  options = {},
  maxRetries = 3
) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(endpoint, options);
      
      if (response.status === 429) { // Rate limited
        const delay = Math.pow(2, attempt - 1) * 1000;
        await new Promise(r => setTimeout(r, delay));
        continue;
      }
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      if (attempt === maxRetries) throw error;
      
      // Exponential backoff
      const delay = Math.pow(2, attempt - 1) * 1000;
      await new Promise(r => setTimeout(r, delay));
    }
  }
}
```

---

## Loading & Skeleton States

```javascript
function PredictionCard({ loading, data }) {
  if (loading) {
    return <SkeletonLoader />;
  }
  
  return (
    <div className="prediction-card">
      <h3>{data.medicine_name}</h3>
      <Metric label="AMC" value={data.x1_amc} />
      <ConfidenceBadge value={data.llm_confidence} />
      <RiskFlagIndicator flags={data.llm_risk_flags} />
    </div>
  );
}
```

---

## Performance Optimization

### 1. Lazy Loading
```javascript
const PredictionDetails = lazy(() => 
  import('./PredictionDetails')
);
```

### 2. Pagination
```javascript
// Endpoint supports pagination
GET /predictions?page=1&limit=20
```

### 3. Caching
```javascript
const cache = new Map();

async function getCachedPrediction(medicineId) {
  if (cache.has(medicineId)) {
    return cache.get(medicineId);
  }
  
  const data = await fetch(`/predictions/${medicineId}`);
  cache.set(medicineId, data);
  return data;
}
```

### 4. Image/Chart Optimization
```javascript
// Use chart libraries with built-in optimization
import { LineChart } from 'recharts';

<LineChart data={usageData} width={800} height={300} />
```

---

## Notification System

```javascript
// Toast notifications for user feedback
const notificationSystem = {
  success: (message) => showToast(message, 'success'),
  error: (message) => showToast(message, 'error'),
  warning: (message) => showToast(message, 'warning'),
  info: (message) => showToast(message, 'info')
};

// Usage
try {
  await generatePrediction(medicineId);
  notificationSystem.success('Prediction generated successfully');
} catch (error) {
  notificationSystem.error(error.message);
}
```

---

## Browser Compatibility & Offline Support

### 1. Service Worker for Offline Support
```javascript
// Register service worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
```

### 2. LocalStorage for Temporary Data
```javascript
// Cache predictions locally
localStorage.setItem(
  `predictions_${hospitalId}`,
  JSON.stringify(predictions)
);
```

---

## Security Considerations

### 1. CORS Configuration
```javascript
// Backend should allow specific origins
headers: {
  'Access-Control-Allow-Origin': 'https://frontend.domain.com',
  'Access-Control-Allow-Credentials': 'true'
}
```

### 2. Token Management
```javascript
// Store token securely
sessionStorage.setItem('access_token', token); // More secure than localStorage
```

### 3. XSS Prevention
```javascript
// Always sanitize user input
const sanitizedInput = DOMPurify.sanitize(userInput);
```

### 4. CSRF Protection
```javascript
// Include CSRF token in requests
headers: {
  'X-CSRF-Token': csrfToken
}
```

---

## Testing Integration

### 1. Unit Tests
```javascript
describe('Predictions API', () => {
  it('should fetch predictions successfully', async () => {
    const data = await generatePrediction('MED001');
    expect(data.success).toBe(true);
    expect(data.prediction).toBeDefined();
  });
});
```

### 2. Integration Tests
```javascript
describe('Prediction Dashboard', () => {
  it('should display predictions after fetching', async () => {
    render(<PredictionDashboard />);
    await waitFor(() => {
      expect(screen.getByText(/150 predictions/i)).toBeInTheDocument();
    });
  });
});
```

---

## Deployment Checklist

- [ ] API endpoint URLs configured correctly
- [ ] Authentication tokens properly managed
- [ ] Error handling implemented
- [ ] Loading states added
- [ ] Performance optimizations applied
- [ ] Security measures in place
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Browser compatibility verified
- [ ] Accessibility compliance checked

---

## Support & Documentation

- **API Documentation:** http://backend:8000/docs
- **ReDoc:** http://backend:8000/redoc
- **Backend Repo:** [Link to backend repo]
- **Frontend Repo:** [Link to frontend repo]
- **Issue Tracker:** [Link to issue tracker]

