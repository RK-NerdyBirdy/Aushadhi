from sqlalchemy import Column, VARCHAR, Integer, DATE, TIMESTAMP, ForeignKey, CheckConstraint, func
from app.database import Base


class HospitalUsage(Base):
    __tablename__ = "hospital_usage"
    
    usage_id = Column(Integer, primary_key=True)
    hospital_id = Column(VARCHAR(50), nullable=False)
    usage_date = Column(DATE, nullable=False, default=func.current_date())
    medicine_id = Column(VARCHAR(50), nullable=False)
    medicine_name = Column(VARCHAR(255), nullable=False)
    quantity_consumed = Column(Integer, nullable=False)
    department = Column(VARCHAR(100))
    created_at = Column(TIMESTAMP, default=func.now())
    
    __table_args__ = (
        CheckConstraint('quantity_consumed >= 0', name='ck_usage_quantity_positive'),
    )
