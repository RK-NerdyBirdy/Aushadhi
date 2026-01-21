# 🚀 Getting Started - Hospital Drug Inventory System

## Prerequisites

Before you begin, ensure you have:
- **Python 3.10 or higher** (`python --version`)
- **PostgreSQL 14+** installed and running
- **Git** for version control
- A code editor (VS Code recommended)

---

## Step 1: Clone/Navigate to Project

```bash
# Navigate to the backend directory
cd c:\robomaneet\projects\aushadhi\backend
```

---

## Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn
- SQLAlchemy & PostgreSQL driver
- Pydantic for validation
- JWT authentication
- pandas & numpy for data processing
- scikit-learn for clustering
- And other required packages

---

## Step 4: Setup Database Connection

### Option A: Local PostgreSQL

```bash
# Create a new PostgreSQL database
createdb drug_inventory

# Update .env file with your credentials
```

### Option B: Use Connection String

Edit `.env` file:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/drug_inventory
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENVIRONMENT=development
```

**Example for local setup:**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/drug_inventory
SECRET_KEY=dev-secret-key-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENVIRONMENT=development
```

---

## Step 5: Initialize Database

This will create all tables and seed sample data:

```bash
python scripts/init_db.py
```

**Expected output:**
```
==================================================
Hospital Drug Inventory System - DB Setup
==================================================
Creating database tables...
✓ Tables created successfully
Seeding sample data...
✓ Sample data created successfully

✓ Database initialization complete!

Next steps:
1. Start the server: uvicorn app.main:app --reload
2. Visit: http://localhost:8000/docs
3. Login with credentials above
```

---

## Step 6: Start the Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

## Step 7: Access the API

### API Documentation (Interactive)
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Test Health Check
```bash
curl http://localhost:8000/health
```

---

## Step 8: Login & Get Token

### 1. Use Swagger UI (Recommended)
1. Go to http://localhost:8000/docs
2. Click on `POST /api/auth/login`
3. Click "Try it out"
4. Enter credentials:
   ```json
   {
     "user_email": "admin@hospital.com",
     "user_password": "password123"
   }
   ```
5. Click "Execute"
6. Copy the `access_token` from response

### 2. Use curl
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "admin@hospital.com",
    "user_password": "password123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "USR001",
  "user_name": "Dr. Sharma",
  "hospital_id": "HOSP001",
  "user_role": "hospital_admin"
}
```

---

## Step 9: Test API Endpoints

### Get Current User
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Upload Stock CSV

First, create a file `stock.csv`:
```csv
medicine_id,medicine_name,medicine_quantity,medicine_expiry
MED001,Paracetamol 500mg,5000,2025-12-31
MED002,Amoxicillin 250mg,1200,2025-06-30
```

Then upload:
```bash
curl -X POST "http://localhost:8000/api/hospital/upload_stock" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@stock.csv"
```

### Calculate Predictions
```bash
curl -X POST "http://localhost:8000/api/hospital/calculate-predictions" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"recalculate_all": true}'
```

### Get Recommendations
```bash
curl -X GET "http://localhost:8000/api/hospital/procurement/recommendations" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Get Dashboard Summary
```bash
curl -X GET "http://localhost:8000/api/hospital/dashboard/summary" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Sample Test Data Included

When you run `init_db.py`, the system creates:

### Hospital
- **ID**: HOSP001
- **Name**: Apollo Hospital Delhi

### Default User
- **Email**: admin@hospital.com
- **Password**: password123
- **Role**: hospital_admin

### Sample Medicines
- MED001: Paracetamol 500mg
- MED002: Amoxicillin 250mg
- MED003: Metformin 500mg
- MED004: Amlodipine 5mg
- MED005: Insulin Glargine 100IU

### Initial Stock
Each medicine has sample inventory and usage data for testing.

---

## Troubleshooting

### Issue: "Connection refused" on Database

**Solution**:
```bash
# Check if PostgreSQL is running
# Windows: Services -> PostgreSQL
# macOS: brew services list
# Linux: sudo systemctl status postgresql

# Verify connection string in .env
# Format: postgresql://user:password@host:port/database
```

### Issue: "ModuleNotFoundError"

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check virtual environment is activated
which python  # macOS/Linux
where python  # Windows
```

### Issue: "Table already exists"

**Solution**:
```bash
# Drop and recreate database
dropdb drug_inventory
createdb drug_inventory
python scripts/init_db.py
```

### Issue: "Port 8000 already in use"

**Solution**:
```bash
# Use different port
uvicorn app.main:app --reload --port 8001

# Or kill process using port 8000
# Windows: netstat -ano | findstr :8000
# macOS/Linux: lsof -i :8000
```

---

## Project Structure Quick Reference

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database setup
│   ├── models/              # Database models
│   ├── schemas/             # Request/Response schemas
│   ├── api/endpoints/       # API routes
│   ├── services/            # Business logic
│   ├── utils/               # Utilities
│   └── core/                # Configuration
├── scripts/
│   └── init_db.py          # Database initialization
├── requirements.txt         # Dependencies
├── .env                     # Configuration
└── README.md               # Documentation
```

---

## Development Workflow

### 1. Make Code Changes
Edit files in `app/` directory

### 2. Server Auto-Reloads
With `--reload` flag, changes auto-reload

### 3. Check API Docs
Go to http://localhost:8000/docs to see updated endpoints

### 4. Test Changes
Use Swagger UI or curl commands

### 5. View Database
```bash
# Connect to PostgreSQL
psql -U postgres drug_inventory

# View tables
\dt

# Query data
SELECT * FROM hospital_stock;
```

---

## Next Steps

After initial setup:

1. **Upload Real Data**
   - Prepare stock.csv with your medicines
   - Prepare usage.csv with consumption history
   - Upload via `/api/hospital/upload_stock` and `/api/hospital/upload_usage`

2. **Review Predictions**
   - Call `/api/hospital/calculate-predictions` to generate X1-X4
   - View at `/api/hospital/predictions`

3. **Check Recommendations**
   - Get reorder suggestions at `/api/hospital/procurement/recommendations`
   - Place orders via `/api/hospital/procurement/create-order`

4. **Monitor Dashboard**
   - View metrics at `/api/hospital/dashboard/summary`
   - Track alerts at `/api/hospital/alerts`

---

## Useful Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Install new package
pip install package_name

# Generate requirements.txt
pip freeze > requirements.txt

# Run tests (when available)
pytest tests/

# Format code
black app/

# Check code quality
flake8 app/
```

---

## Documentation Files

- **README.md** - Main project documentation
- **IMPLEMENTATION_SUMMARY.md** - Detailed implementation overview
- **API Docs** - http://localhost:8000/docs (interactive)

---

## Support

If you encounter issues:

1. Check the error message in terminal
2. Review `.env` configuration
3. Verify PostgreSQL is running
4. Check database connection
5. Review API documentation at `/docs`

---

**Ready to start? Run these commands:**

```bash
# Activate environment
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Initialize database
python scripts/init_db.py

# Start server
uvicorn app.main:app --reload

# Open browser to http://localhost:8000/docs
```

Then login with:
- **Email**: admin@hospital.com
- **Password**: password123

🎉 **You're ready to go!**
