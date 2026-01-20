import json
import re
from llm.groq_client import GroqClient
from llm.output_schema import LLMQuantityPrediction


class LLMRunner:
    def __init__(self, system_prompt, forecast_prompt, constraints_prompt):
        self.client = GroqClient()
        self.system_prompt = system_prompt
        self.forecast_prompt = forecast_prompt
        self.constraints_prompt = constraints_prompt

    def _extract_json(self, text: str) -> dict:
        cleaned = re.sub(r"```json|```", "", text).strip()
        return json.loads(cleaned)

    def run(
        self,
        *,
        context: str,
        organization_id: str,
        medicine_id: str,
        forecast_days: int
    ):
        user_prompt = (
            self.forecast_prompt
            + f"\n\nForecast period: {forecast_days} days\n"
            + self.constraints_prompt
            + "\n\nContext:\n"
            + context
            + "\n\nIMPORTANT: Return ONLY JSON."
        )

        raw_output = self.client.generate(
            self.system_prompt,
            user_prompt
        )

        print("====== RAW LLM OUTPUT ======")
        print(raw_output)
        print("====== END LLM OUTPUT ======")

        try:
            parsed = self._extract_json(raw_output)
        except Exception as e:
            raise ValueError(f"LLM output normalization failed: {e}")

        parsed["organization_id"] = organization_id
        parsed["medicine_id"] = medicine_id
        parsed["forecast_days"] = forecast_days
        return LLMQuantityPrediction(**parsed)