import json
import re
from rag_llm_service.llm.groq_client import GroqClient
from rag_llm_service.llm.output_schema import LLMQuantityPrediction

class LLMRunner:
    def __init__(self, system_prompt, forecast_prompt, constraints_prompt):
        self.client = GroqClient()
        self.system_prompt = system_prompt
        self.forecast_prompt = forecast_prompt
        self.constraints_prompt = constraints_prompt

    def _extract_json(self, text: str) -> dict:
        cleaned = re.sub(r"```json|```", "", text).strip()
        parsed = json.loads(cleaned)

        factor = parsed.get("adjustment_factor", 1.0)

        if not isinstance(factor, (int, float)):
            raise ValueError("Invalid adjustment_factor")

        return {
            "adjustment_factor": max(0.8, min(1.3, float(factor))),
            "confidence": parsed.get("confidence", 0.5),
            "assumptions": parsed.get("assumptions", []),
            "risk_flags": parsed.get("risk_flags", [])
        }

    def run(self, *, context: str, baseline_json: dict) -> LLMQuantityPrediction:
        user_prompt = f"""
{self.forecast_prompt}

{self.constraints_prompt}

BASELINE_FORECAST:
{json.dumps(baseline_json, indent=2)}

CONTEXT:
{context}

IMPORTANT:
- Do NOT change daily structure
- Only suggest adjustment_factor between 0.8 and 1.3
- Return ONLY JSON
"""

        raw = self.client.generate(self.system_prompt, user_prompt)

        parsed = self._extract_json(raw)
        return LLMQuantityPrediction(**parsed)
