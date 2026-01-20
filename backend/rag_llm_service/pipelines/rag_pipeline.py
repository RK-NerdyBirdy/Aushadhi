from retrieval.context_builder import ContextBuilder
from retrieval.ranker import rank_context
from llm.llm_runner import LLMRunner

class RAGPipeline:
    def __init__(self, system_prompt, forecast_prompt, constraints_prompt):
        self.context_builder = ContextBuilder()
        self.llm = LLMRunner(
            system_prompt,
            forecast_prompt,
            constraints_prompt
        )

    def run(self, hospital_id, medicine_id):
        context = self.context_builder.build_context(
            hospital_id,
            medicine_id
        )

        ranked_context = rank_context([context])
        final_context = ranked_context[0]

        return self.llm.run(
            final_context,
            hospital_id,
            medicine_id
        )
