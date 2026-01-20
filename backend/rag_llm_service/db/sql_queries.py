"""
SQL queries for the RAG LLM service.
"""

USAGE_SUMMARY_QUERY = """
SELECT 
    medicine_id,
    medicine_name,
    SUM(usage_amount) as total_usage,
    MIN(usage_date) as first_usage_date,
    MAX(usage_date) as last_usage_date
FROM 
    hospital_usage
WHERE 
    hospital_id = %s AND medicine_id = %s
GROUP BY 
    medicine_id, medicine_name;
"""

STOCK_QUERY = """
SELECT 
    medicine_id,
    medicine_name,
    medicine_expiry,
    medicine_quantity
FROM 
    hospital_stock
WHERE 
    hospital_id = %s AND medicine_id = %s;
"""

PREDICTION_INPUTS_QUERY = """
SELECT 
    x1_amc,
    x2_prescriptions,
    x3_cdpr,
    x4_cv,
    lead_time,
    safety_stock,
    reorder_stock,
    max_stock,
    daily_holding_charges
FROM 
    hospital_predictions
WHERE 
    hospital_id = %s AND medicine_id = %s;
"""

MEDICINE_INFO_QUERY = """
SELECT 
    medicine_name,
    medicine_price,
    cold_storage,
    abc_category,
    ved_category,
    salt_composition,
    pack_size
FROM 
    medicine_info
WHERE 
    hospital_id = %s AND medicine_id = %s;
"""

RECENT_ORDERS_QUERY = """
SELECT 
    order_id,
    medicine_name,
    medicine_quantity_predicted,
    recieved_quantity,
    expected_delivery_date,
    actual_delivery_date,
    order_status
FROM 
    orders
WHERE 
    hospital_id = %s AND medicine_id = %s
ORDER BY 
    expected_delivery_date DESC
LIMIT 10;
"""
