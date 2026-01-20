USAGE_SUMMARY_QUERY = """
SELECT
    hu.hospital_id,
    hu.medicine_id,
    mi.medicine_name,
    AVG(hu.quantity_available) AS avg_quantity_available
FROM hospital_usage hu
JOIN medicine_info mi
  ON hu.hospital_id = mi.hospital_id
 AND hu.medicine_id = mi.medicine_id
WHERE hu.hospital_id = %s
  AND hu.medicine_id = %s
GROUP BY hu.hospital_id, hu.medicine_id, mi.medicine_name;
"""

STOCK_QUERY = """
SELECT
    hs.medicine_quantity,
    hs.medicine_expiry
FROM hospital_stock hs
WHERE hs.hospital_id = %s
  AND hs.medicine_id = %s;
"""

PREDICTION_INPUTS_QUERY = """
SELECT
    hp.X1_amc,
    hp.lead_time,
    hp.safety_stock,
    hp.reorder_stock,
    hp.X4_CV
FROM hospital_predictions hp
WHERE hp.hospital_id = %s
  AND hp.medicine_id = %s;
"""

MEDICINE_INFO_QUERY = """
SELECT
    medicine_price,
    cold_storage,
    abc_category,
    ved_category,
    salt_composition,
    pack_size
FROM medicine_info
WHERE hospital_id = %s
  AND medicine_id = %s;
"""

RECENT_ORDERS_QUERY = """
SELECT
    order_status,
    medicine_quantity_predicted,
    recieved_quantity,
    expected_delivery_date,
    actual_delivery_date
FROM orders
WHERE hospital_id = %s
  AND medicine_id = %s
ORDER BY expected_delivery_date DESC
LIMIT 3;
"""
