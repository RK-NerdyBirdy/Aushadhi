import psycopg2
import psycopg2.extras
import pandas as pd
from datetime import date, timedelta
import random

DATABASE_URL = "postgresql://neondb_owner:npg_0DNlsGkxoym8@ep-green-meadow-a1cjrpsu-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
CSV_PATH = r"C:\Users\aakas\OneDrive\Desktop\comprehensive_inventory_dataset2.csv"

HOSPITAL_ID = "HOSP001"
BATCH_SIZE = 1000

def truncate(val, length):
    if val is None:
        return None
    return str(val)[:length]

print("Loading CSV...")
df = pd.read_csv(CSV_PATH)
print(f"Total rows: {len(df)}")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute(
    """
    INSERT INTO organizations (organization_id, organization_name, organization_type)
    VALUES (%s,%s,%s)
    ON CONFLICT (organization_id) DO NOTHING
    """,
    (HOSPITAL_ID, "Primary General Hospital", "HOSPITAL")
)
conn.commit()

print("Starting fast batch insertion...")

for start in range(0, len(df), BATCH_SIZE):
    end = min(start + BATCH_SIZE, len(df))
    batch = df.iloc[start:end]

    print(f"Inserting batch {start + 1} → {end}")

    medicine_rows = []
    stock_rows = []
    usage_rows = []
    prediction_rows = []

    for _, row in batch.iterrows():
        medicine_id = f"MED{int(row['id']):06d}"
        medicine_name = truncate(row["name"], 255)
        pack_size = truncate(row["pack_size_label"], 50)

        salts = []
        if pd.notna(row.get("short_composition1")):
            salts.append(str(row["short_composition1"]))
        if pd.notna(row.get("short_composition2")):
            salts.append(str(row["short_composition2"]))
        if pd.notna(row.get("salt_composition")):
            salts.append(str(row["salt_composition"]))

        salt_composition = truncate(", ".join(set(salts)), 50)

        medicine_rows.append((
            HOSPITAL_ID,
            medicine_id,
            medicine_name,
            float(row["price"]),
            bool(row["is_cold_storage"]),
            truncate(row["abc_category"], 1),
            truncate(row["ved_category"], 1),
            salt_composition,
            pack_size
        ))

        stock_rows.append((
            HOSPITAL_ID,
            medicine_id,
            medicine_name,
            date.today() + timedelta(days=random.randint(180, 900)),
            random.randint(200, 5000)
        ))

        usage_rows.append((
            HOSPITAL_ID,
            medicine_id,
            medicine_name,
            random.randint(50, 1200)
        ))

        prediction_rows.append((
            HOSPITAL_ID,
            medicine_id,
            medicine_name,
            row["X1_AMC"],
            int(row["X2_Prescriptions"]),
            row["X3_CDPR"],
            row["X4_CV"],
            int(row["lead_time_L"]),
            int(row["safety_stock"]),
            int(row["s_reorder_point"]),
            int(row["S_max_stock"]),
            row["daily_holding_cost"]
        ))

    psycopg2.extras.execute_values(
        cur,
        """
        INSERT INTO medicine_info
        (hospital_id, medicine_id, medicine_name, medicine_price,
         cold_storage, abc_category, ved_category,
         salt_composition, pack_size)
        VALUES %s
        ON CONFLICT (hospital_id, medicine_id) DO NOTHING
        """,
        medicine_rows
    )

    psycopg2.extras.execute_values(
        cur,
        """
        INSERT INTO hospital_stock
        (hospital_id, medicine_id, medicine_name,
         medicine_expiry, medicine_quantity)
        VALUES %s
        ON CONFLICT (hospital_id, medicine_id) DO NOTHING
        """,
        stock_rows
    )

    psycopg2.extras.execute_values(
        cur,
        """
        INSERT INTO hospital_usage
        (hospital_id, medicine_id, medicine_name, quantity_available)
        VALUES %s
        ON CONFLICT (hospital_id, medicine_id) DO NOTHING
        """,
        usage_rows
    )

    psycopg2.extras.execute_values(
        cur,
        """
        INSERT INTO hospital_predictions
        (hospital_id, medicine_id, medicine_name,
         X1_amc, X2_prescriptions, X3_CDPR, X4_CV,
         lead_time, safety_stock, reorder_stock,
         max_stock, daily_holding_charges)
        VALUES %s
        ON CONFLICT (hospital_id, medicine_id) DO NOTHING
        """,
        prediction_rows
    )

    conn.commit()
    print(f"Batch {start + 1} → {end} committed")

cur.close()
conn.close()

print("All data inserted successfully.")
