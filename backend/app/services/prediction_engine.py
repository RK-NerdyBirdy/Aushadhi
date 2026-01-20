import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from app.models.medicine import MedicineInfo
from app.models.stock import HospitalStock
from app.models.usage import HospitalUsage
from app.models.prediction import HospitalPrediction
from app.utils.calculations import (
    calculate_safety_stock,
    calculate_reorder_point,
    calculate_eoq,
    calculate_max_stock,
    calculate_daily_holding_cost,
    calculate_daily_demand_std,
)


class PredictionEngine:
    """Service for AI prediction calculations"""
    
    # Chronic disease keywords for X3_CDPR calculation
    CHRONIC_KEYWORDS = [
        'metformin', 'insulin', 'glimepiride', 'glipizide',  # Diabetes
        'amlodipine', 'atenolol', 'losartan', 'enalapril',   # Hypertension
        'levothyroxine', 'thyroxine',                         # Thyroid
        'salbutamol', 'montelukast', 'fluticasone',          # Asthma
        'clopidogrel', 'aspirin', 'atorvastatin',            # Cardiovascular
    ]
    
    @staticmethod
    def calculate_x1_amc(usage_data: pd.DataFrame) -> dict:
        """
        Calculate X1: Average Monthly Consumption
        X1 = Sum of monthly consumption / number of months
        """
        if usage_data.empty:
            return {}
        
        # Group by medicine and month
        usage_data['month'] = pd.to_datetime(usage_data['usage_date']).dt.to_period('M')
        
        monthly_consumption = usage_data.groupby(['medicine_id', 'month'])['quantity_consumed'].sum()
        amc = monthly_consumption.groupby('medicine_id').mean()
        
        return amc.to_dict()
    
    @staticmethod
    def calculate_x2_prescriptions(usage_data: pd.DataFrame) -> dict:
        """
        Calculate X2: Monthly Average Prescriptions
        X2 = Count of prescription records per month (average)
        """
        if usage_data.empty:
            return {}
        
        usage_data['month'] = pd.to_datetime(usage_data['usage_date']).dt.to_period('M')
        
        monthly_prescriptions = usage_data.groupby(['medicine_id', 'month']).size()
        avg_prescriptions = monthly_prescriptions.groupby('medicine_id').mean()
        
        return avg_prescriptions.to_dict()
    
    @staticmethod
    def calculate_x3_cdpr(medicine_data: pd.DataFrame, usage_data: pd.DataFrame) -> dict:
        """
        Calculate X3: Chronic Disease Prescription Ratio
        X3 = Chronic prescriptions / Total prescriptions
        """
        if usage_data.empty or medicine_data.empty:
            return {}
        
        # Identify chronic medicines
        medicine_data['is_chronic'] = medicine_data['salt_composition'].fillna('').str.lower().apply(
            lambda x: any(keyword in str(x) for keyword in PredictionEngine.CHRONIC_KEYWORDS)
        )
        
        chronic_medicines = set(medicine_data[medicine_data['is_chronic']]['medicine_id'])
        
        # Calculate total and chronic usage
        total_usage = usage_data.groupby('medicine_id')['quantity_consumed'].sum()
        
        chronic_usage = usage_data[
            usage_data['medicine_id'].isin(chronic_medicines)
        ].groupby('medicine_id')['quantity_consumed'].sum()
        
        # Calculate ratio
        cdpr = {}
        for medicine_id in total_usage.index:
            chronic_qty = chronic_usage.get(medicine_id, 0)
            total_qty = total_usage[medicine_id]
            cdpr[medicine_id] = (chronic_qty / total_qty) if total_qty > 0 else 0.1
        
        return cdpr
    
    @staticmethod
    def calculate_x4_cv(usage_data: pd.DataFrame) -> dict:
        """
        Calculate X4: Coefficient of Variation
        X4 = Standard Deviation / Mean
        Measures demand volatility
        """
        if usage_data.empty:
            return {}
        
        usage_data['month'] = pd.to_datetime(usage_data['usage_date']).dt.to_period('M')
        
        monthly_consumption = usage_data.groupby(['medicine_id', 'month'])['quantity_consumed'].sum()
        
        stats = monthly_consumption.groupby('medicine_id').agg(['mean', 'std'])
        
        cv = {}
        for medicine_id in stats.index:
            mean = stats.loc[medicine_id, 'mean']
            std = stats.loc[medicine_id, 'std']
            cv[medicine_id] = (std / mean) if mean > 0 else 0.1
        
        return cv
    
    @staticmethod
    def apply_clustering(
        x1_dict: dict,
        x2_dict: dict,
        x3_dict: dict,
        x4_dict: dict
    ) -> dict:
        """
        Apply K-Means clustering to group medicines
        4 clusters based on research paper
        """
        if not x1_dict:
            return {}
        
        # Prepare data
        medicine_ids = list(x1_dict.keys())
        
        X1 = np.array([x1_dict.get(mid, 0) for mid in medicine_ids])
        X2 = np.array([x2_dict.get(mid, 0) for mid in medicine_ids])
        X3 = np.array([x3_dict.get(mid, 0.1) for mid in medicine_ids])
        X4 = np.array([x4_dict.get(mid, 0.1) for mid in medicine_ids])
        
        # Combine features
        features = np.column_stack([X1, X2, X3, X4])
        
        # Standardize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Apply K-Means
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(features_scaled)
        
        # Map medicine_id to cluster
        cluster_map = {}
        for medicine_id, cluster in zip(medicine_ids, clusters):
            cluster_map[medicine_id] = int(cluster) + 1  # Clusters 1-4 instead of 0-3
        
        return cluster_map
    
    @staticmethod
    def calculate_predictions(
        hospital_id: str,
        db: Session,
        medicine_ids: list = None
    ) -> dict:
        """
        Main prediction calculation orchestration
        """
        start_time = datetime.utcnow()
        
        # Fetch data
        medicine_query = db.query(MedicineInfo).filter(
            MedicineInfo.hospital_id == hospital_id
        )
        
        if medicine_ids:
            medicine_query = medicine_query.filter(MedicineInfo.medicine_id.in_(medicine_ids))
        
        medicines = medicine_query.all()
        
        if not medicines:
            return {
                "success": False,
                "message": "No medicines found",
                "medicines_analyzed": 0,
                "clusters_formed": {}
            }
        
        # Get usage data for last 12 months
        usage_date_cutoff = datetime.utcnow() - timedelta(days=365)
        usage_data_records = db.query(HospitalUsage).filter(
            HospitalUsage.hospital_id == hospital_id,
            HospitalUsage.created_at >= usage_date_cutoff
        ).all()
        
        # Convert to DataFrame
        medicine_df = pd.DataFrame([
            {
                'medicine_id': m.medicine_id,
                'salt_composition': m.salt_composition
            }
            for m in medicines
        ])
        
        usage_df = pd.DataFrame([
            {
                'medicine_id': u.medicine_id,
                'usage_date': u.usage_date,
                'quantity_consumed': u.quantity_consumed
            }
            for u in usage_data_records
        ])
        
        # Calculate X1-X4
        x1_amc = PredictionEngine.calculate_x1_amc(usage_df)
        x2_prescriptions = PredictionEngine.calculate_x2_prescriptions(usage_df)
        x3_cdpr = PredictionEngine.calculate_x3_cdpr(medicine_df, usage_df)
        x4_cv = PredictionEngine.calculate_x4_cv(usage_df)
        
        # Apply clustering
        cluster_map = PredictionEngine.apply_clustering(x1_amc, x2_prescriptions, x3_cdpr, x4_cv)
        
        # Calculate inventory parameters and save
        predictions = []
        cluster_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        
        for medicine in medicines:
            med_id = medicine.medicine_id
            
            if med_id not in x1_amc:
                continue
            
            amc = float(x1_amc.get(med_id, 0))
            prescriptions = int(x2_prescriptions.get(med_id, 0))
            cdpr = float(x3_cdpr.get(med_id, 0.1))
            cv = float(x4_cv.get(med_id, 0.1))
            cluster = cluster_map.get(med_id, 1)
            
            # Calculate inventory parameters
            lead_time = 3  # Default lead time in days
            
            daily_demand_std = calculate_daily_demand_std(amc, cv)
            safety_stock = calculate_safety_stock(daily_demand_std, lead_time)
            reorder_point = calculate_reorder_point(amc, lead_time, safety_stock)
            
            annual_demand = amc * 12
            eoq = calculate_eoq(annual_demand, float(medicine.medicine_price))
            max_stock = calculate_max_stock(reorder_point, eoq)
            
            daily_holding_cost = calculate_daily_holding_cost(float(medicine.medicine_price))
            
            # Create prediction record
            prediction = HospitalPrediction(
                hospital_id=hospital_id,
                medicine_id=med_id,
                medicine_name=medicine.medicine_name,
                X1_amc=amc,
                X2_prescriptions=prescriptions,
                X3_CDPR=cdpr,
                X4_CV=cv,
                lead_time=lead_time,
                safety_stock=safety_stock,
                reorder_stock=reorder_point,
                max_stock=max_stock,
                daily_holding_charges=daily_holding_cost,
                cluster_group=cluster
            )
            
            predictions.append(prediction)
            cluster_counts[cluster] += 1
        
        # Save to database (upsert)
        for pred in predictions:
            existing = db.query(HospitalPrediction).filter(
                HospitalPrediction.hospital_id == hospital_id,
                HospitalPrediction.medicine_id == pred.medicine_id
            ).first()
            
            if existing:
                # Update
                for key, value in {
                    'X1_amc': pred.X1_amc,
                    'X2_prescriptions': pred.X2_prescriptions,
                    'X3_CDPR': pred.X3_CDPR,
                    'X4_CV': pred.X4_CV,
                    'safety_stock': pred.safety_stock,
                    'reorder_stock': pred.reorder_stock,
                    'max_stock': pred.max_stock,
                    'daily_holding_charges': pred.daily_holding_charges,
                    'cluster_group': pred.cluster_group
                }.items():
                    setattr(existing, key, value)
            else:
                db.add(pred)
        
        db.commit()
        
        calculation_time = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            "success": True,
            "message": "Predictions calculated successfully",
            "medicines_analyzed": len(predictions),
            "clusters_formed": {f"group_{k}": v for k, v in cluster_counts.items()},
            "calculation_time_seconds": round(calculation_time, 2)
        }
