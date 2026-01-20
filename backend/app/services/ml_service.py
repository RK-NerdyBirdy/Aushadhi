import httpx
from typing import List, Dict, Any
from app.core.config import settings

class MLServiceClient:
    """Client to interact with external ML service for predictions"""
    
    def __init__(self):
        self.base_url = settings.ML_SERVICE_URL
        self.api_key = settings.ML_SERVICE_API_KEY
    
    async def get_predictions(self, hospital_id: str) -> List[Dict[str, Any]]:
        """
        Fetch predictions from external ML service for a hospital
        
        Returns predictions in this format:
        [
            {
                "hospital_id": "H001",
                "medicine_id": "M001",
                "medicine_name": "Paracetamol",
                "X1_amc": 150.25,
                "X2_prescriptions": 200,
                "X3_CDPR": 0.15,
                "X4_CV": 0.25,
                "lead_time": 7,
                "safety_stock": 50,
                "reorder_stock": 100,
                "max_stock": 300,
                "daily_holding_charges": 0.5
            }
        ]
        """
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/predictions/{hospital_id}",
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error fetching predictions: {e}")
            return []
    
    async def trigger_prediction_generation(self, hospital_id: str) -> Dict[str, Any]:
        """
        Trigger the ML service to generate new predictions for a hospital
        """
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/generate-predictions",
                    headers=headers,
                    json={"hospital_id": hospital_id},
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error triggering prediction generation: {e}")
            return {"status": "error", "message": str(e)}

ml_service = MLServiceClient()
