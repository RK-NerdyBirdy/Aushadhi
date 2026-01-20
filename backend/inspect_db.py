#!/usr/bin/env python3
"""
Database Schema Inspector - Get all table descriptions
"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Parse connection string
db_url = os.getenv('DATABASE_URL')
parsed = urlparse(db_url)

connection_params = {
    'host': parsed.hostname,
    'port': parsed.port or 5432,
    'database': parsed.path.lstrip('/').split('?')[0],  # Handle query params
    'user': parsed.username,
    'password': parsed.password,
}

print(f"Connecting to: {connection_params['host']}:{connection_params['port']}/{connection_params['database']}")

try:
    conn = psycopg2.connect(**connection_params)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    tables = ['alerts', 'hospital_predictions', 'hospital_stock', 'medicine_info', 'orders', 'organizations', 'users']
    
    for table in tables:
        print(f"\n{'='*80}")
        print(f"Table: {table}")
        print('='*80)
        
        # Get table info
        cur.execute(f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table,))
        
        columns = cur.fetchall()
        
        if not columns:
            print(f"  [Table does not exist or has no columns]")
            continue
        
        # Get constraints
        cur.execute(f"""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_name = %s
        """, (table,))
        
        constraints = cur.fetchall()
        
        # Print columns
        print("\nColumns:")
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" default {col['column_default']}" if col['column_default'] else ""
            print(f"  {col['column_name']:<30} {col['data_type']:<20} {nullable:<10}{default}")
        
        # Print constraints
        if constraints:
            print("\nConstraints:")
            for constraint in constraints:
                print(f"  {constraint['constraint_name']:<40} {constraint['constraint_type']}")
        
        # Get foreign keys
        cur.execute(f"""
            SELECT DISTINCT
                rc.constraint_name,
                kcu1.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.referential_constraints rc
            JOIN information_schema.key_column_usage kcu1 
                ON rc.constraint_name = kcu1.constraint_name 
                AND rc.constraint_schema = kcu1.table_schema
            JOIN information_schema.constraint_column_usage ccu 
                ON rc.unique_constraint_name = ccu.constraint_name
            WHERE kcu1.table_name = %s
        """, (table,))
        
        fks = cur.fetchall()
        if fks:
            print("\nForeign Keys:")
            for fk in fks:
                print(f"  {fk['constraint_name']}: {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
    
    cur.close()
    conn.close()
    print(f"\n{'='*80}\n✅ Database inspection completed\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
