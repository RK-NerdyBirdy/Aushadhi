# Aushadhi - Multi-Hospital Medicine Inventory Management System

A comprehensive FastAPI-based backend system for managing medicine inventory across multiple healthcare organizations, with integration to external ML services for demand prediction.

## Overview

Aushadhi is a modern, scalable solution for:
- **Multi-tenant inventory management** across hospitals/clinics
- **Real-time stock tracking** with expiry date monitoring
- **Predictive analytics** integration from external ML services
- **Order management** with approval workflows
- **Alert system** for low stock, overstock, and expiry warnings
- **Comprehensive reporting** and analytics

## Tech Stack

- **Python 3.9+**
- **FastAPI 0.100+** - Modern web framework
- **PostgreSQL 14+** - Relational database
- **SQLAlchemy 2.0** - ORM
- **Pydantic 2.0** - Data validation
- **JWT** - Authentication
- **Alembic** - Database migrations

## Project Structure

```
aushadhi-backend/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── database.py             # Database configuration
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── crud/                   # CRUD operations
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/      # API endpoints
│   ├── core/                   # Config, security, utils
│   ├── services/               # ML, alerts, reports
│   └── middleware/             # Auth, error handling
├── alembic/                    # Database migrations
├── tests/                      # Test files
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation & Setup

### 1. Clone and Install Dependencies

```bash
cd pharma
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

### 2. Setup Database

Create PostgreSQL database:
```sql
CREATE DATABASE aushadhi_db;
```

Update `.env` with your database credentials:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/aushadhi_db
```

### 3. Run Database Migrations

```bash
alembic upgrade head
```

### 4. Start the Application

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at `http://localhost:8000`

## API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Key Features

### 1. Authentication & Authorization
- JWT-based authentication
- Role-based access control (Admin, Manager, Pharmacist, Viewer)
- Multi-tenancy with hospital isolation

### 2. Medicine Inventory Management
- Master data management per hospital
- ABC-VED classification
- Cold storage tracking
- Composite pricing

### 3. Stock Management
- Real-time stock levels
- Expiry date tracking
- Low stock alerts
- FIFO principles

### 4. Predictive Analytics
- Integration with external ML service
- Demand forecasting metrics (AMC, CDPR, CV)
- Safety stock calculations
- Reorder point optimization

### 5. Order Management
- Automated reorder suggestions
- Order status tracking (pending, approved, in_transit, delivered, cancelled)
- Delivery date monitoring
- Quantity variance tracking

### 6. Alert System
- Low stock alerts
- Expiry warnings (90, 60, 30 days)
- Overstock alerts
- Order delay alerts
- Customizable alert management

### 7. Reporting & Analytics
- Inventory reports
- Consumption analysis
- Financial reports
- ABC analysis
- VED analysis
- Expiry reports

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/change-password` - Change password

### Organizations
- `GET /api/v1/organizations` - List all organizations
- `POST /api/v1/organizations` - Create organization
- `GET /api/v1/organizations/{id}` - Get organization details
- `PUT /api/v1/organizations/{id}` - Update organization
- `DELETE /api/v1/organizations/{id}` - Delete organization

### Users
- `GET /api/v1/users` - List users
- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{id}` - Get user
- `PUT /api/v1/users/{id}` - Update user
- `PATCH /api/v1/users/{id}/deactivate` - Deactivate user

### Medicines
- `GET /api/v1/medicines` - List medicines
- `POST /api/v1/medicines` - Add medicine
- `GET /api/v1/medicines/{id}` - Get medicine
- `PUT /api/v1/medicines/{id}` - Update medicine
- `DELETE /api/v1/medicines/{id}` - Remove medicine

### Stock Management
- `GET /api/v1/stock` - List stock
- `POST /api/v1/stock` - Add stock entry
- `GET /api/v1/stock/low-stock/list` - Get low stock medicines
- `GET /api/v1/stock/expiring/list` - Get expiring medicines
- `PATCH /api/v1/stock/{id}/adjust` - Adjust stock quantity

### Usage Tracking
- `GET /api/v1/usage` - Get usage records
- `POST /api/v1/usage` - Record usage
- `GET /api/v1/usage/date-range/query` - Usage within date range
- `GET /api/v1/usage/analytics/trends` - Usage analytics

### Predictions
- `GET /api/v1/predictions` - List predictions
- `POST /api/v1/predictions/sync` - Sync from ML service
- `GET /api/v1/predictions/reorder-alerts/list` - Reorder alerts

### Orders
- `GET /api/v1/orders` - List orders
- `POST /api/v1/orders` - Create order
- `PATCH /api/v1/orders/{id}/status` - Update status
- `PATCH /api/v1/orders/{id}/receive` - Mark as received

### Alerts
- `GET /api/v1/alerts` - List alerts
- `POST /api/v1/alerts` - Create alert
- `PATCH /api/v1/alerts/{id}/resolve` - Resolve alert
- `PATCH /api/v1/alerts/{id}/dismiss` - Dismiss alert

### Dashboard & Reports
- `GET /api/v1/dashboard` - Dashboard overview
- `GET /api/v1/reports/inventory` - Inventory report
- `GET /api/v1/reports/consumption` - Consumption report
- `GET /api/v1/reports/financial` - Financial report
- `GET /api/v1/reports/abc-analysis` - ABC analysis
- `GET /api/v1/reports/ved-analysis` - VED analysis

## Database Schema

### Core Tables
1. **organizations** - Hospital/clinic information
2. **users** - User accounts and roles
3. **medicine_info** - Master medicine catalog (per hospital)
4. **hospital_stock** - Current inventory levels
5. **hospital_usage** - Daily consumption tracking
6. **hospital_predictions** - ML predictions
7. **orders** - Procurement orders
8. **alerts** - System notifications

## Configuration

### Environment Variables (.env)
```env
# Application
APP_NAME=Aushadhi API
DEBUG=True
PORT=8000

# Database
DATABASE_URL=postgresql://user:pass@localhost/aushadhi_db

# Security
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# External ML Service
ML_SERVICE_URL=http://localhost:8001
ML_SERVICE_API_KEY=your-api-key

# Alerts
EXPIRY_WARNING_DAYS=90,60,30
```

## ML Service Integration

The system integrates with an external ML service for:
- Demand forecasting (AMC - Average Monthly Consumption)
- Statistical metrics (CDPR, CV - Coefficient of Variation)
- Safety stock calculations
- Reorder point optimization
- Maximum stock determination

The ML service should provide a REST API at `ML_SERVICE_URL` that accepts:
- `GET /predictions/{hospital_id}` - Fetch predictions
- `POST /generate-predictions` - Trigger prediction generation

## Testing

Run tests with pytest:
```bash
pytest
pytest --cov=app  # With coverage
pytest tests/test_auth.py  # Specific test file
```

## Development Guidelines

### Code Style
- Follow PEP 8 conventions
- Use type hints throughout
- Document complex business logic

### Adding New Endpoints
1. Create schema in `app/schemas/`
2. Create CRUD operations in `app/crud/`
3. Create endpoint in `app/api/v1/endpoints/`
4. Include router in `app/api/v1/api.py`
5. Add tests in `tests/`

### Database Changes
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Security Best Practices

- ✅ JWT authentication with expiration
- ✅ Password hashing with bcrypt
- ✅ Multi-tenant data isolation
- ✅ Role-based access control
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention (ORM)
- ✅ CORS configuration

## Common Tasks

### Add New Medicine Category
```python
# In your data migration
from app.crud import medicine
medicine.create(db, obj_in=MedicineCreate(...))
```

### Generate Predictions from ML
```python
from app.services import ml_service
predictions = await ml_service.get_predictions(hospital_id="H001")
```

### Create Low Stock Alert
```python
from app.services import alert_service
alert_service.check_low_stock_alerts(db, hospital_id="H001")
```

## Troubleshooting

### Database Connection Error
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists and credentials are correct

### JWT Validation Failed
- Check SECRET_KEY is set properly
- Verify token expiration (ACCESS_TOKEN_EXPIRE_MINUTES)
- Ensure Authorization header format: `Bearer <token>`

### ML Service Connection Error
- Verify ML_SERVICE_URL is accessible
- Check ML_SERVICE_API_KEY is correct
- Ensure ML service is running

## Performance Optimization

- ✅ Composite primary keys for efficient multi-tenant queries
- ✅ Database indexing on frequently queried fields
- ✅ Pagination for large result sets
- ✅ Connection pooling with SQLAlchemy
- ✅ Async API calls to external services

## Deployment

### Production Checklist
- [ ] Set DEBUG=False
- [ ] Change SECRET_KEY to strong random value
- [ ] Use PostgreSQL (not SQLite)
- [ ] Setup HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Setup logging and monitoring
- [ ] Use strong database passwords
- [ ] Setup CI/CD pipeline
- [ ] Setup backup strategy

## Support & Documentation

For detailed API documentation, visit `/docs` after starting the application.

## License

Proprietary - All rights reserved

## Contributing

Internal development only. Follow code standards and submit PR for review.

---

**Version**: 1.0.0  
**Last Updated**: January 2026  
**Maintainer**: Development Team
