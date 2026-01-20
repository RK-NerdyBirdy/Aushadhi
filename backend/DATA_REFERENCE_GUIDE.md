# Dashboard & Reports - Data Reference Guide

## Database Models Used

### Core Models Referenced

#### 1. HospitalStock (Stock Model)
```
Columns:
  - hospital_id (VARCHAR)
  - medicine_id (VARCHAR) 
  - medicine_name (VARCHAR)
  - medicine_expiry (DATE)
  - medicine_quantity (INTEGER)

Primary Key: (hospital_id, medicine_id)
```

#### 2. MedicineInfo (Medicine Model)
```
Columns:
  - hospital_id (VARCHAR)
  - medicine_id (VARCHAR)
  - medicine_name (VARCHAR)
  - medicine_price (NUMERIC)
  - cold_storage (BOOLEAN)
  - abc_category (VARCHAR) - 'A', 'B', 'C'
  - ved_category (VARCHAR) - 'V', 'E', 'D'
  - salt_composition (TEXT)
  - pack_size (VARCHAR)

Primary Key: (hospital_id, medicine_id)
```

#### 3. HospitalUsage (Usage Model)
```
Columns:
  - hospital_id (VARCHAR)
  - usage_date (DATE)
  - medicine_id (VARCHAR)
  - medicine_name (VARCHAR)
  - usage_amount (INTEGER)

Primary Key: (hospital_id, medicine_id)
```

#### 4. Order (Orders Model)
```
Columns:
  - order_id (INTEGER, auto-increment)
  - hospital_id (VARCHAR)
  - medicine_id (VARCHAR)
  - medicine_name (VARCHAR)
  - medicine_quantity_predicted (INTEGER)
  - recieved_quantity (INTEGER)
  - expected_delivery_date (DATE)
  - actual_delivery_date (DATE)
  - order_status (VARCHAR) - 'pending', 'delivered', 'cancelled'
  - medicine_price (NUMERIC)
  - created_at (TIMESTAMP)

Primary Key: order_id
```

#### 5. Alert (Alerts Model)
```
Columns:
  - alert_id (INTEGER, auto-increment)
  - hospital_id (VARCHAR)
  - medicine_id (VARCHAR)
  - alert_type (VARCHAR) - 'low_stock', 'expiry', 'order', etc.
  - alert_message (TEXT)
  - alert_status (VARCHAR) - 'active', 'resolved'
  - created_at (TIMESTAMP)
  - resolved_at (TIMESTAMP)

Primary Key: alert_id
```

#### 6. HospitalPrediction (Predictions Model)
```
Columns:
  - hospital_id (VARCHAR)
  - medicine_id (VARCHAR)
  - medicine_name (VARCHAR)
  - X1_amc (NUMERIC) - Average Monthly Consumption
  - X2_prescriptions (INTEGER)
  - X3_cdpr (NUMERIC) - Consumption to Diagnosis Ratio
  - X4_cv (NUMERIC) - Coefficient of Variation
  - lead_time (INTEGER)
  - safety_stock (INTEGER)
  - reorder_stock (INTEGER)
  - max_stock (INTEGER)
  - daily_holding_charges (NUMERIC)

Primary Key: (hospital_id, medicine_id)
```

---

## Endpoint Data Reference

### Dashboard Endpoints

#### 1. GET `/api/v1/dashboard/`
**Database Tables Used:**
- HospitalStock (main)
- MedicineInfo (for pricing)
- HospitalUsage (for 7-day trends)
- Order (for pending orders)
- Alert (for active alerts)

**Data Extracted:**
```python
{
    "summary": {
        "total_medicines": COUNT(DISTINCT stock.medicine_id),
        "total_stock_value": SUM(stock.quantity * medicine.price),
        "low_stock_count": COUNT(WHERE stock.quantity < safety_stock),
        "expired_count": COUNT(WHERE expiry_date < TODAY),
        "expiring_soon_count": COUNT(WHERE expiry_date BETWEEN TODAY AND TODAY+90d),
        "pending_orders_count": COUNT(WHERE status = 'pending'),
        "pending_orders_value": SUM(predicted_qty * price WHERE status='pending'),
        "active_alerts_count": COUNT(WHERE status = 'active')
    },
    "usage_metrics": {
        "total_usage_7_days": SUM(usage.amount WHERE date >= TODAY-7d),
        "avg_daily_usage": total_usage / 7
    },
    "top_medicines": [stock items sorted by quantity DESC LIMIT 5],
    "top_usage": [usage items grouped by medicine_id SUM(amount) DESC LIMIT 5],
    "recent_alerts": [alerts sorted by created_at DESC LIMIT 5]
}
```

#### 2. GET `/api/v1/dashboard/inventory-health`
**Database Tables Used:**
- HospitalStock
- HospitalUsage (implied)

**Data Extracted:**
```python
{
    "health_score": FLOAT(0-100),  # 100 - (problem_count / total_count * 100)
    "status": STRING,               # 'good'|'warning'|'critical'
    "total_medicines": COUNT(*),
    "low_stock_medicines": COUNT(WHERE quantity < threshold),
    "expired_medicines": COUNT(WHERE expiry_date < TODAY),
    "expiring_soon_medicines": COUNT(WHERE expiry_date < TODAY+30d),
}
```

#### 3. GET `/api/v1/dashboard/stock-distribution`
**Database Tables Used:**
- HospitalStock
- MedicineInfo (for abc_category)

**Data Extracted:**
```python
{
    "distribution": {
        "A": SUM(quantity WHERE abc_category='A'),
        "B": SUM(quantity WHERE abc_category='B'),
        "C": SUM(quantity WHERE abc_category='C'),
        "unclassified": SUM(quantity WHERE abc_category IS NULL)
    }
}
```

---

### Reports Endpoints

#### 1. GET `/api/v1/reports/inventory`
**Database Tables Used:**
- HospitalStock (main)
- MedicineInfo (for pricing & category)

**Data Extracted:**
```python
{
    "report_type": "inventory",
    "generated_at": TIMESTAMP,
    "total_medicines": COUNT(*),
    "total_inventory_value": SUM(quantity * price),
    "data": [
        {
            "medicine_id": stock.medicine_id,
            "medicine_name": stock.medicine_name,
            "quantity": stock.quantity,
            "price_per_unit": medicine.price,
            "total_value": quantity * price,
            "expiry_date": stock.expiry_date,
            "days_to_expiry": (expiry_date - TODAY).days,
            "status": "expired"|"expiring_soon"|"active",
            "category": medicine.abc_category
        }
    ]
}
```

#### 2. GET `/api/v1/reports/consumption`
**Database Tables Used:**
- HospitalUsage (main)

**Date Parameters:**
- start_date: defaults to TODAY-30days
- end_date: defaults to TODAY

**Data Extracted:**
```python
{
    "report_type": "consumption",
    "period": {"start": DATE, "end": DATE},
    "total_consumption": SUM(usage.amount),
    "daily_average": total_consumption / days_in_range,
    "data": [
        {
            "medicine_id": usage.medicine_id,
            "medicine_name": usage.medicine_name,
            "total_usage": SUM(usage.amount),
            "usage_days": COUNT(DISTINCT usage_date),
            "avg_daily_usage": total_usage / days_in_range
        }
    ]
}
```

#### 3. GET `/api/v1/reports/financial`
**Database Tables Used:**
- HospitalStock (for valuation)
- MedicineInfo (for pricing)
- Order (for spending analysis)

**Data Extracted:**
```python
{
    "report_type": "financial",
    "timestamp": TIMESTAMP,
    "stock": {
        "total_inventory_value": SUM(stock.quantity * medicine.price),
        "total_medicines": COUNT(*)
    },
    "orders": {
        "total_spent": SUM(price * received_qty WHERE status='delivered'),
        "pending_value": SUM(price * predicted_qty WHERE status='pending'),
        "delivered_count": COUNT(WHERE status='delivered'),
        "average_order_cost": total_spent / delivered_count
    },
    "financial_health": {
        "working_capital": total_inventory_value,
        "pending_obligations": pending_value
    }
}
```

#### 4. GET `/api/v1/reports/abc-analysis`
**Database Tables Used:**
- MedicineInfo (main, filtered by abc_category)
- HospitalStock (for quantities)

**Data Extracted:**
```python
{
    "report_type": "abc_analysis",
    "description": "Classification based on value and importance",
    "data": {
        "A": [medicines with abc_category='A'],
        "B": [medicines with abc_category='B'],
        "C": [medicines with abc_category='C'],
        "unclassified": [medicines where abc_category IS NULL]
    }
}
```

#### 5. GET `/api/v1/reports/ved-analysis`
**Database Tables Used:**
- MedicineInfo (main, filtered by ved_category)
- HospitalStock (for quantities)

**Data Extracted:**
```python
{
    "report_type": "ved_analysis",
    "description": "Classification based on criticality",
    "data": {
        "V": [medicines with ved_category='V'],
        "E": [medicines with ved_category='E'],
        "D": [medicines with ved_category='D'],
        "unclassified": [medicines where ved_category IS NULL]
    }
}
```

#### 6. GET `/api/v1/reports/expiry`
**Database Tables Used:**
- HospitalStock (main)

**Query Parameters:**
- days: threshold for "expiring soon" (default: 90)

**Data Extracted:**
```python
{
    "report_type": "expiry",
    "days_threshold": 90,
    "summary": {
        "expired_count": COUNT(WHERE expiry_date < TODAY),
        "expiring_soon_count": COUNT(WHERE expiry_date BETWEEN TODAY AND TODAY+days)
    },
    "expired": [
        {
            "medicine_id": stock.medicine_id,
            "medicine_name": stock.medicine_name,
            "quantity": stock.quantity,
            "expiry_date": stock.expiry_date,
            "days_until_expiry": (expiry_date - TODAY).days
        }
    ],
    "expiring_soon": [same structure, sorted by days_until_expiry ASC]
}
```

#### 7. GET `/api/v1/reports/stock-valuation`
**Database Tables Used:**
- HospitalStock (main)
- MedicineInfo (for pricing)

**Data Extracted:**
```python
{
    "report_type": "stock_valuation",
    "total_inventory_value": SUM(quantity * price),
    "high_value_items": [
        {
            "medicine_id": stock.medicine_id,
            "medicine_name": stock.medicine_name,
            "quantity": stock.quantity,
            "value": quantity * price
        }
    ],  # Top 10 by value DESC
    "slow_moving_items": [
        {
            "medicine_id": stock.medicine_id,
            "medicine_name": stock.medicine_name,
            "quantity": stock.quantity,
            "value": quantity * price
        }
    ]  # Top 10 by quantity ASC (< 10 units)
}
```

---

## Query Patterns Used

### Aggregation Queries
- **SUM**: For total values, total quantities, total costs
- **COUNT**: For item counts, distinct medicine counts
- **GROUP BY**: For category-wise distribution, medicine-wise summaries
- **ORDER BY**: For ranking by value, quantity, or date

### Date Queries
- **TODAY**: datetime.now().date()
- **DATE RANGES**: Between filters for consumption periods
- **DAYS CALCULATION**: (target_date - today).days

### Filtering
- **hospital_id**: All queries filtered by current user's hospital
- **status**: For orders, alerts (pending, active, delivered, resolved)
- **categories**: ABC (A/B/C), VED (V/E/D), medicine categories
- **expiry_date**: For expiry calculations and status determination

### Joins
- Stock + Medicine: For pricing and category info
- Stock + Usage: For consumption analysis
- Stock + Order: For pending obligations
- Stock + Alert: For active issues

---

## Schema Validation Checklist

✅ All database models properly defined in `app/models/`
✅ CRUD operations available for all models in `app/crud/`
✅ Dashboard endpoints use appropriate aggregations
✅ Reports endpoints filter by hospital_id
✅ Date calculations use datetime.now().date()
✅ Decimal types used for financial calculations
✅ Response schemas match Pydantic models in `app/schemas/`
✅ All endpoints secured with JWT authentication
✅ Multi-hospital access controlled via check_hospital_access()

---

## Performance Considerations

1. **Large Datasets**: Use LIMIT in queries for top N items
2. **Aggregations**: Database-side aggregation faster than Python
3. **Date Ranges**: Restrict consumption reports to specific date range
4. **Indexing**: Ensure hospital_id and medicine_id are indexed
5. **Query Optimization**: Use select() for specific columns when possible

---

## Future Enhancements

- [ ] Caching frequently accessed reports
- [ ] Scheduled report generation
- [ ] Real-time dashboard updates via WebSockets
- [ ] Export to CSV/PDF with proper formatting
- [ ] Advanced filtering options
- [ ] Time-series analysis and predictions
