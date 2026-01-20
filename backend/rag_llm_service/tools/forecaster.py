import json
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from statsmodels.tsa.statespace.sarimax import SARIMAX

load_dotenv()

DB_URL = os.getenv("DB_URL", "")

try:
    db_engine = create_engine(DB_URL)
    print("✅ Database engine initialized.")
except Exception as e:
    raise RuntimeError(f"❌ Failed to connect to database: {e}")

def get_medicine_forecast(medicine_id: str, hospital_id: int, forecast_days: int = 14) -> str:
    """
    Forecasting tool that predicts the required quantity of a specific medicine 
    for the next few days using real data from the PostgreSQL database.
    
    Args:
        medicine_name (str): The exact name of the medicine.
        hospital_id (int): The unique ID of the hospital.
        forecast_days (int): The number of days in the future to forecast. Default: 14

    Returns:
        str: JSON string with daily predictions and cumulative total.
    """
    
    # Hardcoded SARIMA Hyperparameters (Optimized for yearly seasonality)
    ORDER = (0, 1, 1)
    SEASONAL_ORDER = (1, 0, 1, os.getenv("SEASONALITY", 7))

    try:
        query = text("""
            SELECT usage_date, usage_amount 
            FROM hospital_usage 
            WHERE medicine_id = :med_id 
              AND hospital_id = :hosp_id
            ORDER BY usage_date ASC
        """)
        
        with db_engine.connect() as connection:
            df = pd.read_sql(query, connection, params={"med_id": medicine_id, "hosp_id": hospital_id})

        if df.empty:
            return json.dumps({
                "error": f"No historical usage found for '{medicine_id}' at hospital {hospital_id}."
            })
        
        if len(df) < forecast_days:
            return json.dumps({
                "error": f"Insufficient data ({len(df)} rows). Need at least 14 days of history."
            })

        df['usage_date'] = pd.to_datetime(df['usage_date'])
        df = df.set_index('usage_date')
        
        series = df['usage_amount'].asfreq('D').fillna(0)

        model = SARIMAX(
            series,
            order=ORDER,
            seasonal_order=SEASONAL_ORDER,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        model_fit = model.fit(disp=False)

        forecast = model_fit.get_forecast(steps=forecast_days)
        predicted_mean = forecast.predicted_mean

        results = []
        running_total = 0
        
        for date, qty in predicted_mean.items():
            daily_qty = max(0, int(round(qty))) 
            running_total += daily_qty
            
            results.append({
                "date": date.strftime("%Y-%m-%d"),
                "predicted_quantity": daily_qty,
                "cumulative_total": running_total
            })

        return json.dumps({
            "medicine": medicine_id,
            "hospital_id": hospital_id,
            "forecast_period": f"{forecast_days} Days",
            "total_predicted_demand": running_total,
            "data": results
        })

    except Exception as e:
        return json.dumps({"error": f"Internal Prediction Error: {str(e)}"})

if __name__ == "__main__":
    TEST_MED_ID = "MED000001" 
    TEST_HOSPITAL_ID = "HOSP001"

    print(f"🚀 Testing forecast for: {TEST_MED_ID}...")
    response = get_medicine_forecast(TEST_MED_ID, TEST_HOSPITAL_ID)
    
    # Pretty print the JSON output
    parsed = json.loads(response)
    print(json.dumps(parsed, indent=2))