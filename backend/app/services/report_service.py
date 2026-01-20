from sqlalchemy.orm import Session

class ReportService:
    """Service for generating reports"""
    
    @staticmethod
    def generate_inventory_report(db: Session, hospital_id: str):
        """Generate inventory report"""
        from app.crud import stock as stock_crud
        all_stock = stock_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
        return {"medicines": len(all_stock)}
    
    @staticmethod
    def generate_consumption_report(db: Session, hospital_id: str):
        """Generate consumption report"""
        from app.crud import usage as usage_crud
        from datetime import date
        usage_data = usage_crud.get_by_date_range(
            db,
            hospital_id=hospital_id,
            start_date=date(date.today().year, 1, 1),
            end_date=date.today()
        )
        return {"usage_records": len(usage_data)}
    
    @staticmethod
    def generate_financial_report(db: Session, hospital_id: str):
        """Generate financial report"""
        from decimal import Decimal
        from app.crud import stock as stock_crud, medicine as medicine_crud
        
        all_stock = stock_crud.get_multi(db, hospital_id=hospital_id, skip=0, limit=99999)
        total_value = Decimal('0')
        
        for stock in all_stock:
            med = medicine_crud.get(db, hospital_id=hospital_id, medicine_id=stock.medicine_id)
            if med:
                total_value += stock.medicine_quantity * med.medicine_price
        
        return {"total_stock_value": float(total_value)}

report_service = ReportService()
