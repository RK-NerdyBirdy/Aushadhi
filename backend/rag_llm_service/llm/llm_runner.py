"""
LLM Runner for generating insights using Groq and RAG.
"""
from dotenv import load_dotenv
load_dotenv()
import os
from groq import Groq

from rag_llm_service.db.neon_client import NeonClient
from rag_llm_service.db.row_to_text import build_context_block

class LLMRunner:
    """
    A class to run the RAG-powered LLM to generate insights.
    """
    def __init__(self):
        """
        Initializes the LLMRunner with a NeonClient and a Groq client.
        """
        self.neon_client = NeonClient()
        
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_model = os.getenv("GROQ_MODEL", "llama3-70b-8192")
        self.groq_temperature = float(os.getenv("GROQ_TEMPERATURE", 0.2))
        self.groq_max_tokens = int(os.getenv("GROQ_MAX_TOKENS", 1024))
        
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable not set.")
            
        self.groq_client = Groq(api_key=self.groq_api_key)

    def generate_prompt(self, user_query: str, context_data: str) -> str:
        """
        Generates a detailed prompt for the LLM.
        """
        system_prompt = (
            "You are an expert AI assistant for a hospital inventory management system called 'Aushadhi'. "
            "Your task is to answer questions about medicine inventory, demand, and predictions. "
            "You will be provided with a user query and a context block containing relevant data from the database. "
            "Analyze the data in the context block carefully to provide a comprehensive and data-driven answer. "
            "If the context is empty, state that you don't have enough information to answer the question."
            "Do not make up information that is not present in the context."
        )
        
        human_prompt = (
            f"Here is the data context for the user's query:\n\n"
            f"{context_data}\n\n"
            f"User Query: {user_query}\n\n"
            "Please provide a detailed answer based on the data provided."
        )
        
        return f"{system_prompt}\n\n{human_prompt}"

    def run(self, user_query: str, hospital_id: str, medicine_id: str) -> str:
        """
        Runs the RAG pipeline for a given query and medicine.
        
        1. Fetches data from the database.
        2. Builds the context block.
        3. Generates the prompt.
        4. Calls the LLM.
        5. Returns the response.
        """
        if not self.neon_client.pool:
            return "Error: Database connection is not available."
            
        # 1. Fetch data
        context_data_dict = self.neon_client.get_context_data(hospital_id, medicine_id)
        
        # 2. Build context block
        context_block = build_context_block(**context_data_dict)
        
        if not context_block:
            return "I do not have enough information to answer this question. The database returned no data for the specified medicine."
            
        # 3. Generate prompt
        prompt = self.generate_prompt(user_query, context_block)
        
        # 4. Call LLM
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.groq_model,
                temperature=self.groq_temperature,
                max_tokens=self.groq_max_tokens,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"An error occurred while communicating with the LLM: {e}"

    def close(self):
        """
        Closes the NeonClient connection.
        """
        self.neon_client.close()

if __name__ == '__main__':
    # This requires GROQ_API_KEY and DATABASE_URL to be set as environment variables
    # Example usage (for testing)
    
    # Make sure to set your environment variables, for example:
    # export GROQ_API_KEY="your_groq_api_key"
    # export DATABASE_URL="postgresql://user:pass@host:port/db"

    try:
        llm_runner = LLMRunner()
        
        test_query = "What is the current stock and predicted demand for this medicine?"
        # Replace with a valid hospital_id and medicine_id from your database
        test_hospital_id = "H001"
        test_medicine_id = "M001"
        
        response = llm_runner.run(test_query, test_hospital_id, test_medicine_id)
        
        print("--- LLM Response ---")
        print(response)
        
        llm_runner.close()
    except ValueError as e:
        print(e)
    except ImportError:
        print("Please install necessary libraries: pip install groq psycopg")
