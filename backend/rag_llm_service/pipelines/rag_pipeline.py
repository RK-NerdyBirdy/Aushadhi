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


class RAGPipeline:
    def __init__(self):
        self.db = NeonClient()
        self.llm = LLMRunner()

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
            usage_summary=usage,
            stock_levels=stock[0] if stock else None,
            prediction_inputs=prediction,
            medicine_info=medicine,
            recent_orders=orders
        )

        # Generate baseline forecast from current prediction if exists
        baseline = {}
        if prediction:
            baseline = {
                "X1_amc": float(prediction.get('X1_amc', 0)),
                "X2_prescriptions": int(prediction.get('X2_prescriptions', 0)),
                "lead_time": int(prediction.get('lead_time', 0)),
                "safety_stock": int(prediction.get('safety_stock', 0)),
                "reorder_stock": int(prediction.get('reorder_stock', 0)),
                "max_stock": int(prediction.get('max_stock', 0))
            }

        # Get LLM adjustment
        llm_adjustment = self.llm.run(
            context=context,
            baseline_json=baseline
        )

        # Merge baseline with LLM adjustments
        return self._merge_forecasts(baseline, llm_adjustment)
    
    def _merge_forecasts(self, baseline, llm_adjustment):
        """Merge baseline forecast with LLM adjustments"""
        if not isinstance(llm_adjustment, dict):
            try:
                llm_adjustment = json.loads(llm_adjustment)
            except (json.JSONDecodeError, TypeError):
                return baseline
        
        # Combine with LLM adjustments
        result = baseline.copy()
        if 'adjustment_factor' in llm_adjustment:
            result['adjustment_factor'] = llm_adjustment['adjustment_factor']
        if 'confidence' in llm_adjustment:
            result['confidence'] = llm_adjustment['confidence']
        if 'assumptions' in llm_adjustment:
            result['assumptions'] = llm_adjustment['assumptions']
        if 'risk_flags' in llm_adjustment:
            result['risk_flags'] = llm_adjustment['risk_flags']
        
        return result
