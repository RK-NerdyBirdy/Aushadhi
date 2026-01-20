import json
from rag_llm_service.db.neon_client import NeonClient
from rag_llm_service.db.sql_queries import (
    USAGE_SUMMARY_QUERY,
    STOCK_QUERY,
    PREDICTION_INPUTS_QUERY,
    MEDICINE_INFO_QUERY,
    RECENT_ORDERS_QUERY
)
from rag_llm_service.db.row_to_text import build_context_block
from rag_llm_service.llm.llm_runner import LLMRunner
from rag_llm_service.tools.forecast import get_medicine_forecast
from rag_llm_service.pipelines.fusion_service import fuse_forecasts


class RAGPipeline:
    def __init__(self, system_prompt, forecast_prompt, constraints_prompt):
        self.db = NeonClient()
        self.llm = LLMRunner(
            system_prompt,
            forecast_prompt,
            constraints_prompt
        )

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
            stock=stock[0] if stock else None,
            prediction=prediction,
            medicine=medicine,
            orders=orders
        )

        baseline_raw = get_medicine_forecast(
            medicine_id=medicine_id,
            hospital_id=hospital_id,
            forecast_days=forecast_days
        )

        baseline = json.loads(baseline_raw)

        llm_adjustment = self.llm.run(
            context=context,
            baseline_json=baseline
        )

        return fuse_forecasts(baseline, llm_adjustment)
