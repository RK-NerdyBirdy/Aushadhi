from rag_llm_service.db.neon_client import NeonClient
from rag_llm_service.db.sql_queries import (
    USAGE_SUMMARY_QUERY,
    STOCK_QUERY,
    PREDICTION_INPUTS_QUERY,
    MEDICINE_INFO_QUERY,
    RECENT_ORDERS_QUERY
)
from db.row_to_text import build_context_block

class ContextBuilder:
    def __init__(self):
        self.db = NeonClient()

    def build_context(self, hospital_id, medicine_id):
        usage = self.db.fetch_one(
            USAGE_SUMMARY_QUERY,
            (hospital_id, medicine_id)
        )

        if not usage:
            raise ValueError("No usage data found for given hospital and medicine")

        stock = self.db.fetch_one(
            STOCK_QUERY,
            (hospital_id, medicine_id)
        )

        prediction = self.db.fetch_one(
            PREDICTION_INPUTS_QUERY,
            (hospital_id, medicine_id)
        )

        medicine = self.db.fetch_one(
            MEDICINE_INFO_QUERY,
            (hospital_id, medicine_id)
        )

        orders = self.db.fetch_all(
            RECENT_ORDERS_QUERY,
            (hospital_id, medicine_id)
        )

        return build_context_block(
            usage=usage,
            stock=stock,
            prediction=prediction,
            medicine=medicine,
            orders=orders
        )
