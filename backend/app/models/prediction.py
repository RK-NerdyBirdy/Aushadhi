from sqlalchemy import Column, String, VARCHAR, INTEGER, NUMERIC, Float, PrimaryKeyConstraint, ForeignKeyConstraint, JSON
from app.database import Base

class HospitalPrediction(Base):
    __tablename__ = "hospital_predictions"
    
    hospital_id = Column(VARCHAR(50), nullable=False)
    medicine_id = Column(VARCHAR(50), nullable=False)
    medicine_name = Column(String(255), nullable=False)
    x1_amc = Column("x1_amc", NUMERIC(12, 4), nullable=True)
    x2_prescriptions = Column("x2_prescriptions", INTEGER, nullable=True)
    x3_cdpr = Column("x3_cdpr", NUMERIC(10, 4), nullable=True)
    x4_cv = Column("x4_cv", NUMERIC(10, 4), nullable=True)
    lead_time = Column(INTEGER, nullable=True)
    safety_stock = Column(INTEGER, nullable=True)
    reorder_stock = Column(INTEGER, nullable=True)
    max_stock = Column(INTEGER, nullable=True)
    daily_holding_charges = Column(NUMERIC(12, 4), nullable=True)
    
    # RAG LLM columns
    llm_confidence = Column(Float, nullable=True, default=0.0)
    llm_assumptions = Column(JSON, nullable=True, default=lambda: [])
    llm_risk_flags = Column(JSON, nullable=True, default=lambda: [])
    
    __table_args__ = (
        PrimaryKeyConstraint('hospital_id', 'medicine_id'),
        ForeignKeyConstraint(['hospital_id', 'medicine_id'], ['medicine_info.hospital_id', 'medicine_info.medicine_id']),
    )
