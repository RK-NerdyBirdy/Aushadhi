from db.neon_client import NeonClient
from db.sql_queries import (
    USAGE_SUMMARY_QUERY,
    STOCK_QUERY,
    PREDICTION_INPUTS_QUERY,
    MEDICINE_INFO_QUERY,
    RECENT_ORDERS_QUERY
)
from db.row_to_text import build_context_block
from llm.llm_runner import LLMRunner


class RAGPipeline:
    def __init__(self, system_prompt, forecast_prompt, constraints_prompt):
        self.db = NeonClient()
        self.llm = LLMRunner(system_prompt, forecast_prompt, constraints_prompt)

    def run(self, hospital_id, medicine_id, forecast_days=14):
        usage = self.db.fetch_one(
            USAGE_SUMMARY_QUERY,
            (hospital_id, medicine_id)
        )

        stock = self.db.fetch_all(
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

        context = build_context_block(
            usage=usage,
            stock=stock,
            prediction=prediction,
            medicine=medicine,
            orders=orders
        )

        return self.llm.run(
            context=context,
            organization_id=hospital_id,
            medicine_id=medicine_id,
            forecast_days=forecast_days
        )
