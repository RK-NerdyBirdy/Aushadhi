#!/usr/bin/env python3
"""
Database Migration - Add missing columns to tables
"""
import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

# Parse connection string
db_url = os.getenv('DATABASE_URL')
from urllib.parse import urlparse
parsed = urlparse(db_url)

connection_params = {
    'host': parsed.hostname,
    'port': parsed.port or 5432,
    'database': parsed.path.lstrip('/').split('?')[0],
    'user': parsed.username,
    'password': parsed.password,
}

print(f"Connecting to: {connection_params['host']}:{connection_params['port']}/{connection_params['database']}")

try:
    conn = psycopg2.connect(**connection_params)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Migration: Add hashed_password to users table
    print("\n📋 Migration 1: Adding hashed_password to users table...")
    try:
        cur.execute("""
            ALTER TABLE users 
            ADD COLUMN hashed_password VARCHAR(255) NOT NULL DEFAULT 'temp_hash';
        """)
        print("✅ Added hashed_password column to users")
    except psycopg2.Error as e:
        if "already exists" in str(e):
            print("⏭️  Column already exists, skipping...")
        else:
            print(f"❌ Error: {e}")
    
    # Migration: Add created_at to orders table
    print("\n📋 Migration 2: Adding created_at to orders table...")
    try:
        cur.execute("""
            ALTER TABLE orders 
            ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
        """)
        print("✅ Added created_at column to orders")
    except psycopg2.Error as e:
        if "already exists" in str(e):
            print("⏭️  Column already exists, skipping...")
        else:
            print(f"❌ Error: {e}")
    
    # Migration: Add hospital_usage table if missing
    print("\n📋 Migration 3: Checking hospital_usage table...")
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS hospital_usage (
                hospital_id VARCHAR(50) NOT NULL,
                usage_date DATE NOT NULL DEFAULT CURRENT_DATE,
                medicine_id VARCHAR(50) NOT NULL,
                medicine_name VARCHAR(255) NOT NULL,
                usage_amount INTEGER NOT NULL,
                PRIMARY KEY (hospital_id, medicine_id),
                FOREIGN KEY (hospital_id, medicine_id) 
                    REFERENCES medicine_info(hospital_id, medicine_id),
                CHECK (usage_amount >= 0)
            );
        """)
        print("✅ hospital_usage table is ready")
    except psycopg2.Error as e:
        if "already exists" in str(e):
            print("⏭️  Table already exists, skipping...")
        else:
            print(f"❌ Error: {e}")
    
    cur.close()
    conn.close()
    print(f"\n{'='*80}\n✅ Migration completed successfully!\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
