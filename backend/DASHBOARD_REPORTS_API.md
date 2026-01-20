# Dashboard and Reports API Documentation

## Overview
The Aushadhi system provides comprehensive dashboard and reporting capabilities for multi-hospital medicine inventory management.

## Dashboard Endpoints

### 1. GET `/api/v1/dashboard/`
**Get comprehensive dashboard overview**

Returns key metrics and insights for the user's hospital:
- Total medicines inventory count
- Total stock valuation
- Low stock medicines count
- Expired medicines count
- Medicines expiring within 90 days
- Pending orders count and value
- Active alerts count
- 7-day usage trends
- Top 5 medicines by stock quantity
- Top 5 medicines by usage
- Recent 5 alerts

**Response:**
```json
{
  "summary": {
    "total_medicines": 150,
    "total_stock_value": 250000.50,
    "low_stock_count": 5,
    "expired_count": 2,
    "expiring_soon_count": 8,
    "pending_orders_count": 3,
    "pending_orders_value": 15000.00,
    "active_alerts_count": 4
  },
  "usage_metrics": {
    "total_usage_7_days": 450,
    "avg_daily_usage": 64.29
  },
  "top_medicines": [...],
  "top_usage": [...],
  "recent_alerts": [...]
}
```

### 2. GET `/api/v1/dashboard/inventory-health`
**Get inventory health score and metrics**

Calculates a health score based on:
- Low stock items
- Expired medicines
- Medicines expiring soon

Status levels:
- **good**: Health score >= 80%
- **warning**: Health score 50-79%
- **critical**: Health score < 50%

**Response:**
```json
{
  "health_score": 85.5,
  "status": "good",
  "total_medicines": 150,
  "low_stock_medicines": 5,
  "expired_medicines": 2,
  "expiring_soon_medicines": 8,
  "recommendations": [
    "Reorder low stock items",
    "Remove expired medicines"
  ]
}
```

### 3. GET `/api/v1/dashboard/stock-distribution`
**Get stock distribution by medicine category**

Shows quantity distribution across ABC categories.

**Response:**
```json
{
  "distribution": {
    "A": 50000,
    "B": 30000,
    "C": 15000,
    "unclassified": 5000
  }
}
```

---

## Reports Endpoints

### 1. GET `/api/v1/reports/inventory`
**Generate comprehensive inventory report**

**Query Parameters:**
- `format`: json|csv|pdf (default: json)
- `hospital_id`: Optional, for admin users to view other hospitals

**Response:**
```json
{
  "report_type": "inventory",
  "generated_at": "2026-01-21T10:30:00",
  "total_medicines": 150,
  "total_inventory_value": 250000.50,
  "data": [
    {
      "medicine_id": "MED001",
      "medicine_name": "Aspirin",
      "quantity": 500,
      "price_per_unit": 10.50,
      "total_value": 5250.00,
      "expiry_date": "2027-06-15",
      "days_to_expiry": 510,
      "status": "active",
      "category": "A"
    }
  ]
}
```

### 2. GET `/api/v1/reports/consumption`
**Generate consumption/usage report**

**Query Parameters:**
- `start_date`: Date in YYYY-MM-DD format (default: 30 days ago)
- `end_date`: Date in YYYY-MM-DD format (default: today)
- `hospital_id`: Optional

**Response:**
```json
{
  "report_type": "consumption",
  "period": {
    "start": "2025-12-22",
    "end": "2026-01-21"
  },
  "total_consumption": 1250,
  "daily_average": 41.67,
  "data": [
    {
      "medicine_id": "MED001",
      "medicine_name": "Aspirin",
      "total_usage": 450,
      "usage_days": 25,
      "avg_daily_usage": 15.0
    }
  ]
}
```

### 3. GET `/api/v1/reports/financial`
**Generate financial analysis report**

Provides:
- Stock valuation
- Total spending on orders
- Pending obligations
- Financial health metrics

**Response:**
```json
{
  "report_type": "financial",
  "timestamp": "2026-01-21T10:30:00",
  "stock": {
    "total_inventory_value": 250000.50,
    "total_medicines": 150
  },
  "orders": {
    "total_spent": 75000.00,
    "pending_value": 15000.00,
    "delivered_count": 45,
    "average_order_cost": 1666.67
  },
  "financial_health": {
    "working_capital": 250000.50,
    "pending_obligations": 15000.00
  }
}
```

### 4. GET `/api/v1/reports/abc-analysis`
**ABC Analysis Report**

Classification based on inventory value and importance:
- **A**: High-value, critical items (70% of value)
- **B**: Medium-value, important items (20% of value)
- **C**: Low-value, non-critical items (10% of value)

**Response:**
```json
{
  "report_type": "abc_analysis",
  "description": "Classification based on value and importance",
  "data": {
    "A": [
      {
        "medicine_id": "MED001",
        "medicine_name": "Aspirin",
        "price": 10.50,
        "quantity_on_hand": 500
      }
    ],
    "B": [...],
    "C": [...],
    "unclassified": [...]
  }
}
```

### 5. GET `/api/v1/reports/ved-analysis`
**VED Analysis Report**

Classification based on criticality:
- **V (Vital)**: Critical for patient care, must always be in stock
- **E (Essential)**: Important but not critical
- **D (Desirable)**: Nice to have, can be substituted

**Response:**
```json
{
  "report_type": "ved_analysis",
  "description": "Classification based on criticality",
  "data": {
    "V": [...],
    "E": [...],
    "D": [...],
    "unclassified": [...]
  }
}
```

### 6. GET `/api/v1/reports/expiry`
**Expiry and Shelf-Life Management Report**

**Query Parameters:**
- `days`: Threshold for "expiring soon" (default: 90 days)
- `hospital_id`: Optional

**Response:**
```json
{
  "report_type": "expiry",
  "days_threshold": 90,
  "summary": {
    "expired_count": 2,
    "expiring_soon_count": 8
  },
  "expired": [
    {
      "medicine_id": "MED001",
      "medicine_name": "Aspirin",
      "quantity": 50,
      "expiry_date": "2025-10-15",
      "days_until_expiry": -98
    }
  ],
  "expiring_soon": [
    {
      "medicine_id": "MED002",
      "medicine_name": "Paracetamol",
      "quantity": 100,
      "expiry_date": "2026-02-15",
      "days_until_expiry": 25
    }
  ]
}
```

### 7. GET `/api/v1/reports/stock-valuation`
**Stock Valuation and Aging Report**

Identifies:
- High-value items (for focused management)
- Slow-moving items (for clearance planning)

**Response:**
```json
{
  "report_type": "stock_valuation",
  "total_inventory_value": 250000.50,
  "high_value_items": [
    {
      "medicine_id": "MED001",
      "medicine_name": "Aspirin",
      "quantity": 500,
      "value": 5250.00
    }
  ],
  "slow_moving_items": [
    {
      "medicine_id": "MED010",
      "medicine_name": "Rare Drug",
      "quantity": 3,
      "value": 500.00
    }
  ]
}
```

---

## Authentication

All endpoints require JWT Bearer token authentication. Use the `/api/v1/auth/login` endpoint to get a token.

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/v1/dashboard/
```

---

## Access Control

- **Hospital Staff**: Can only view their own hospital's data
- **System Admin**: Can view any hospital's data by passing `hospital_id` parameter

---

## Use Cases

### Daily Operations
- Check dashboard for quick overview
- Monitor low stock items
- Track pending orders
- View active alerts

### Weekly Analysis
- Generate consumption report
- Review inventory health
- Check expiry status

### Monthly Planning
- Financial report for budget tracking
- ABC/VED analysis for category reviews
- Stock valuation for asset management
- Consumption trends for reordering

### Quarterly Reviews
- Comprehensive inventory audit
- Year-over-year consumption comparison
- Cost analysis and optimization
- Supplier performance evaluation

---

## Performance Notes

- Reports with large datasets (>1000 items) may take 1-2 seconds
- CSV/PDF export features are in development
- Consider using `start_date` and `end_date` parameters to limit consumption report range for faster queries
