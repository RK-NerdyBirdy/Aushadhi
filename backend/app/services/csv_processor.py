import pandas as pd
from io import BytesIO
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.medicine import MedicineInfo
from app.models.stock import HospitalStock
from app.models.usage import HospitalUsage
from app.utils.validators import validate_csv_stock_format, validate_csv_usage_format


class CSVProcessor:
    """Service for processing CSV uploads"""
    
    @staticmethod
    def process_stock_csv(
        file_content: bytes,
        hospital_id: str,
        db: Session
    ) -> dict:
        """
        Process stock CSV upload
        
        Expected columns: medicine_id, medicine_name, medicine_quantity, medicine_expiry
        """
        try:
            # Parse CSV
            df = pd.read_csv(BytesIO(file_content))
            
            # Validate required columns
            required_columns = {'medicine_id', 'medicine_name', 'medicine_quantity', 'medicine_expiry'}
            is_valid, error_msg = validate_csv_stock_format(
                required_columns,
                set(df.columns)
            )
            
            if not is_valid:
                return {
                    "success": False,
                    "message": error_msg,
                    "records_processed": 0,
                    "records_inserted": 0,
                    "records_updated": 0,
                    "errors": [error_msg]
                }
            
            records_processed = 0
            records_inserted = 0
            records_updated = 0
            errors = []
            
            for idx, row in df.iterrows():
                try:
                    records_processed += 1
                    
                    medicine_id = str(row['medicine_id']).strip()
                    medicine_name = str(row['medicine_name']).strip()
                    medicine_quantity = int(row['medicine_quantity'])
                    medicine_expiry = pd.to_datetime(row['medicine_expiry']).date()
                    
                    # Check if medicine exists in medicine_info
                    medicine = db.query(MedicineInfo).filter(
                        MedicineInfo.hospital_id == hospital_id,
                        MedicineInfo.medicine_id == medicine_id
                    ).first()
                    
                    if not medicine:
                        errors.append(f"Row {idx + 1}: Medicine {medicine_id} not found in master data")
                        continue
                    
                    # Check if stock record exists
                    existing_stock = db.query(HospitalStock).filter(
                        HospitalStock.hospital_id == hospital_id,
                        HospitalStock.medicine_id == medicine_id
                    ).first()
                    
                    if existing_stock:
                        # Update existing record
                        existing_stock.medicine_quantity = medicine_quantity
                        existing_stock.medicine_expiry = medicine_expiry
                        records_updated += 1
                    else:
                        # Insert new record
                        stock = HospitalStock(
                            hospital_id=hospital_id,
                            medicine_id=medicine_id,
                            medicine_name=medicine_name,
                            medicine_quantity=medicine_quantity,
                            medicine_expiry=medicine_expiry
                        )
                        db.add(stock)
                        records_inserted += 1
                
                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")
            
            db.commit()
            
            return {
                "success": True,
                "message": "Stock data uploaded successfully",
                "records_processed": records_processed,
                "records_inserted": records_inserted,
                "records_updated": records_updated,
                "errors": errors
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing CSV: {str(e)}",
                "records_processed": 0,
                "records_inserted": 0,
                "records_updated": 0,
                "errors": [str(e)]
            }
    
    @staticmethod
    def process_usage_csv(
        file_content: bytes,
        hospital_id: str,
        db: Session
    ) -> dict:
        """
        Process usage CSV upload
        
        Expected columns: usage_date, medicine_id, medicine_name, quantity_consumed, department
        """
        try:
            # Parse CSV
            df = pd.read_csv(BytesIO(file_content))
            
            # Validate required columns
            required_columns = {'usage_date', 'medicine_id', 'medicine_name', 'quantity_consumed', 'department'}
            is_valid, error_msg = validate_csv_usage_format(
                required_columns,
                set(df.columns)
            )
            
            if not is_valid:
                return {
                    "success": False,
                    "message": error_msg,
                    "records_processed": 0,
                    "records_inserted": 0,
                    "date_range": {},
                    "errors": [error_msg]
                }
            
            records_processed = 0
            records_inserted = 0
            errors = []
            date_list = []
            
            for idx, row in df.iterrows():
                try:
                    records_processed += 1
                    
                    usage_date = pd.to_datetime(row['usage_date']).date()
                    medicine_id = str(row['medicine_id']).strip()
                    medicine_name = str(row['medicine_name']).strip()
                    quantity_consumed = int(row['quantity_consumed'])
                    # department ignored as per schema
                    
                    # Check if medicine exists
                    medicine = db.query(MedicineInfo).filter(
                        MedicineInfo.hospital_id == hospital_id,
                        MedicineInfo.medicine_id == medicine_id
                    ).first()
                    
                    if not medicine:
                        errors.append(f"Row {idx + 1}: Medicine {medicine_id} not found in master data")
                        continue
                    
                    # Check for duplicates (same hospital, medicine, date)
                    existing = db.query(HospitalUsage).filter(
                        HospitalUsage.hospital_id == hospital_id,
                        HospitalUsage.medicine_id == medicine_id,
                        HospitalUsage.usage_date == usage_date
                    ).first()
                    
                    if not existing:
                        usage = HospitalUsage(
                            hospital_id=hospital_id,
                            usage_date=usage_date,
                            medicine_id=medicine_id,
                            medicine_name=medicine_name,
                            usage_amount=quantity_consumed
                        )
                        db.add(usage)
                        records_inserted += 1
                        date_list.append(usage_date)
                
                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")
            
            db.commit()
            
            # Calculate date range
            date_range = {}
            if date_list:
                date_range = {
                    "start_date": min(date_list).isoformat(),
                    "end_date": max(date_list).isoformat()
                }
            
            return {
                "success": True,
                "message": "Usage data uploaded successfully",
                "records_processed": records_processed,
                "records_inserted": records_inserted,
                "date_range": date_range,
                "errors": errors
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing CSV: {str(e)}",
                "records_processed": 0,
                "records_inserted": 0,
                "date_range": {},
                "errors": [str(e)]
            }
