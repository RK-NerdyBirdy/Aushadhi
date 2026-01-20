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

        parsed = json.loads(cleaned)

        normalized = {
            "llm_predicted_quantity": parsed.get("llm_predicted_quantity")
                or parsed.get("order_quantity"),
            "confidence": parsed.get("confidence", 0.5),
            "assumptions": (
                parsed["assumptions"]
                if isinstance(parsed.get("assumptions"), list)
                else [parsed.get("assumptions", "No assumptions provided")]
            ),
            "risk_flags": parsed.get("risk_flags", [])
        }

        if normalized["llm_predicted_quantity"] is None:
            raise ValueError("LLM response missing quantity field")

        return normalized

    def run(self, context, hospital_id, medicine_id):
        user_prompt = (
            self.forecast_prompt
            + "\n\n"
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

        parsed["hospital_id"] = hospital_id
        parsed["medicine_id"] = medicine_id

        return LLMQuantityPrediction(**parsed)
