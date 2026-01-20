"""
Database client for connecting to NeonDB (PostgreSQL).
"""
import os
import os
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
import psycopg


from rag_llm_service.db.sql_queries import (
    USAGE_SUMMARY_QUERY,
    STOCK_QUERY,
    PREDICTION_INPUTS_QUERY,
    MEDICINE_INFO_QUERY,
    RECENT_ORDERS_QUERY
)

class NeonClient:
    """
    A client for interacting with the NeonDB PostgreSQL database.
    """
    def __init__(self):
        
        """
        Initializes the database client and connection pool.
        """
        try:
            db_url = os.getenv(
                "DATABASE_URL",
                "postgresql://postgres:password@localhost:5432/aushadhi_db"
            )

            self.pool = ConnectionPool(
                conninfo=db_url,
                min_size=2,
                max_size=10,
                kwargs={"row_factory": dict_row}
            )

        except psycopg.OperationalError as e:
            print(f"Error connecting to the database: {e}")
            self.pool = None

    def fetch_data(self, query: str, params: tuple) -> list[dict]:
        """
        Fetches data from the database using a given query and parameters.
        """
        if not self.pool:
            return []
        with self.pool.getconn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                result = cur.fetchall()
                return result if result else []

    def get_context_data(self, hospital_id: str, medicine_id: str) -> dict:
        """
        Retrieves all context data for a specific medicine at a hospital.
        """
        params = (hospital_id, medicine_id)
        
        context_data = {
            "usage_summary": self.fetch_data(USAGE_SUMMARY_QUERY, params),
            "stock_levels": self.fetch_data(STOCK_QUERY, params),
            "prediction_inputs": self.fetch_data(PREDICTION_INPUTS_QUERY, params),
            "medicine_info": self.fetch_data(MEDICINE_INFO_QUERY, params),
            "recent_orders": self.fetch_data(RECENT_ORDERS_QUERY, params),
        }
        
        return context_data
    def fetch_all(self, query: str, params: tuple) -> list[dict]:
        if not self.pool:
            return []
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall() or []


    def fetch_one(self, query: str, params: tuple) -> dict | None:
        if not self.pool:
            return None
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()


    def close(self):
        """
        Closes the database connection pool.
        """
        if self.pool:
            self.pool.close()

if __name__ == '__main__':
    # Example usage (for testing)
    client = NeonClient()
    if client.pool:
        # Replace with a valid hospital_id and medicine_id from your database
        test_hospital_id = "H001"
        test_medicine_id = "M001"
        
        data = client.get_context_data(test_hospital_id, test_medicine_id)
        
        from rag_llm_service.db.row_to_text import build_context_block
        context_block = build_context_block(**data)
        
        print(f"--- Context for Hospital {test_hospital_id}, Medicine {test_medicine_id} ---")
        print(context_block)
        
        client.close()

