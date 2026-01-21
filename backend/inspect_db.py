import psycopg2
import sys

def describe_all_tables(conn_string):
    """
    Connects to a PostgreSQL database and prints the schema for all tables.
    """
    conn = None
    try:
        # Connect to the PostgreSQL database using the connection string
        conn = psycopg2.connect(conn_string)
        # Create a cursor object
        cur = conn.cursor()

        # Query to get all user-defined table names in the 'public' schema
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """)
        
        tables = cur.fetchall()

        if not tables:
            print("No tables found in the 'public' schema.")
            return

        for table in tables:
            table_name = table[0]
            print(f"\n--- Table: {table_name} ---")

            # Query to get column details (name and data type) for the current table
            cur.execute("""
                SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))

            columns = cur.fetchall()
            for col in columns:
                col_name, data_type, max_len, is_nullable, default_val = col
                details = f"  - {col_name}: {data_type}"
                if max_len is not None:
                    details += f"({max_len})"
                details += f" | Nullable: {is_nullable}"
                if default_val is not None:
                    details += f" | Default: {default_val}"
                print(details)

        # Close the cursor and connection
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        sys.exit(1)
    finally:
        if conn is not None:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == '__main__':
    # Replace the placeholder with your actual Neon database connection string
    # The format is typically: "postgresql://user:password@host:port/dbname?sslmode=require"
    neon_conn_string = "postgresql://neondb_owner:npg_Oslv6SAEJex7@ep-snowy-glitter-a17b3nee-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
    
    # !!! IMPORTANT: Replace this with your actual connection string !!!
    # Example: neon_conn_string = "postgresql://alex:secretpassword@ep-cool-stuff-12345.us-east-2.aws.neon.tech/mydb?sslmode=require"

    describe_all_tables(neon_conn_string)
