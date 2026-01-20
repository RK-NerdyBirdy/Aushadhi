# Quick Start Guide - Aushadhi Backend

## 1. Prerequisites
- Python 3.9+
- PostgreSQL 14+
- pip (Python package manager)

## 2. Quick Setup (5 minutes)

### Step 1: Create Virtual Environment
```bash
cd c:\robomaneet\projects\pharma
python -m venv venv
venv\Scripts\activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Setup PostgreSQL Database
```sql
-- Connect to PostgreSQL
CREATE DATABASE aushadhi_db;
```

### Step 4: Configure Environment
Create `.env` file (already included, verify settings):
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/aushadhi_db
SECRET_KEY=your-super-secret-key-change-this
DEBUG=True
```

### Step 5: Start Application
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 6: Access API
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 3. Database Setup (Alternative with Alembic)

```bash
# Run migrations
alembic upgrade head

# Or create fresh
python
from app.database import Base, engine
Base.metadata.create_all(bind=engine)
exit()
```

## 4. First API Call

### Register Organization
```bash
curl -X POST "http://localhost:8000/api/v1/organizations" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "H001",
    "organization_name": "City Hospital",
    "organization_type": "hospital"
  }'
```

### Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "Dr. John",
    "user_email": "john@hospital.com",
    "password": "secure123",
    "hospital_id": "H001",
    "user_role": "admin"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=john@hospital.com&password=secure123"
```

## 5. Running Tests
```bash
pytest                    # Run all tests
pytest -v               # Verbose output
pytest --cov=app        # With coverage report
pytest tests/test_auth.py  # Specific test file
```

## 6. Project Structure Overview

```
pharma/
├── app/
│   ├── main.py              ← FastAPI entry point
│   ├── database.py          ← DB config
│   ├── models/              ← SQLAlchemy models (8 tables)
│   ├── schemas/             ← Pydantic validation schemas
│   ├── crud/                ← Database operations
│   ├── api/v1/endpoints/    ← All 11 endpoint modules
│   ├── core/                ← Config, security, utils
│   └── services/            ← ML, alerts, reports
├── alembic/                 ← Database migrations
├── tests/                   ← Test files
├── .env                     ← Configuration
├── requirements.txt         ← Dependencies
└── README.md               ← Full documentation
```

## 7. Available Endpoints (11 Modules)

- **Auth** - Register, login, password management
- **Organizations** - Hospital/clinic management
- **Users** - User account management
- **Medicines** - Medicine catalog
- **Stock** - Inventory management
- **Usage** - Consumption tracking
- **Predictions** - ML integration
- **Orders** - Procurement management
- **Alerts** - Notifications system
- **Dashboard** - Overview metrics
- **Reports** - Analytics & reporting

## 8. Common Commands

```bash
# Start server (development)
python -m uvicorn app.main:app --reload

# Check database
psql -U postgres -d aushadhi_db

# Create admin user
python
from app.database import SessionLocal
from app.crud.user import user
from app.schemas.user import UserCreate
db = SessionLocal()
admin = user.create(db, UserCreate(...))

# Run specific endpoint
curl http://localhost:8000/api/v1/dashboard
```

## 9. ML Service Integration

If using external ML service:
```env
ML_SERVICE_URL=http://your-ml-service:8001
ML_SERVICE_API_KEY=your-api-key
```

## 10. Troubleshooting

| Issue | Solution |
|-------|----------|
| `Connection refused` | Ensure PostgreSQL is running |
| `Database does not exist` | Run `CREATE DATABASE aushadhi_db` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `Port 8000 in use` | Use `--port 8001` or kill process |

## 11. Next Steps

1. ✅ Explore API docs at `/docs`
2. ✅ Create test data (organizations, users)
3. ✅ Add medicines to catalog
4. ✅ Record stock levels
5. ✅ Setup ML service integration
6. ✅ Configure alerts

## Support

- Full API docs: `/docs`
- Code examples: See `tests/` directory
- Configuration: See `README.md`

---
**Ready to use!** Start the server and access `/docs` to explore all endpoints.
