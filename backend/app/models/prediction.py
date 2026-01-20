from sqlalchemy import Column, String, VARCHAR, INTEGER, NUMERIC, PrimaryKeyConstraint, ForeignKeyConstraint
from app.database import Base

class HospitalPrediction(Base):
    __tablename__ = "hospital_predictions"
    
    hospital_id = Column(VARCHAR(50), nullable=False)
    medicine_id = Column(VARCHAR(50), nullable=False)
    medicine_name = Column(String(255), nullable=False)
    X1_amc = Column(NUMERIC(12, 4), nullable=True)
    X2_prescriptions = Column(INTEGER, nullable=True)
    X3_CDPR = Column(NUMERIC(10, 4), nullable=True)
    X4_CV = Column(NUMERIC(10, 4), nullable=True)
    lead_time = Column(INTEGER, nullable=True)
    safety_stock = Column(INTEGER, nullable=True)
    reorder_stock = Column(INTEGER, nullable=True)
    max_stock = Column(INTEGER, nullable=True)
    daily_holding_charges = Column(NUMERIC(12, 4), nullable=True)
    
    __table_args__ = (
        PrimaryKeyConstraint('hospital_id', 'medicine_id'),
        ForeignKeyConstraint(['hospital_id', 'medicine_id'], ['medicine_info.hospital_id', 'medicine_info.medicine_id']),
    )
