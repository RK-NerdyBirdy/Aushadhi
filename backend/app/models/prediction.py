from sqlalchemy import Column, VARCHAR, Integer, Numeric, TIMESTAMP, ForeignKey, PrimaryKeyConstraint, func
from app.database import Base


class HospitalPrediction(Base):
    __tablename__ = "hospital_predictions"
    
    hospital_id = Column(VARCHAR(50), nullable=False)
    medicine_id = Column(VARCHAR(50), nullable=False)
    medicine_name = Column(VARCHAR(255), nullable=False)
    X1_amc = Column(Numeric(12, 4))
    X2_prescriptions = Column(Integer)
    X3_CDPR = Column(Numeric(10, 4))
    X4_CV = Column(Numeric(10, 4))
    lead_time = Column(Integer)
    safety_stock = Column(Integer)
    reorder_stock = Column(Integer)
    max_stock = Column(Integer)
    daily_holding_charges = Column(Numeric(12, 4))
    cluster_group = Column(Integer)
    last_calculated = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        PrimaryKeyConstraint('hospital_id', 'medicine_id', name='pk_hospital_predictions'),
    )
