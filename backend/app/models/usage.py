from sqlalchemy import Column, VARCHAR, Integer, DATE, ForeignKey, CheckConstraint, PrimaryKeyConstraint
from app.database import Base


class HospitalUsage(Base):
    __tablename__ = "hospital_usage"
    
    hospital_id = Column(VARCHAR(50), ForeignKey("organizations.organization_id"), nullable=False)
    usage_date = Column(DATE, nullable=False)
    medicine_id = Column(VARCHAR(50), nullable=False)
    medicine_name = Column(VARCHAR(255), nullable=False)
    usage_amount = Column(Integer, nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('hospital_id', 'medicine_id', name='pk_hospital_usage'),
        CheckConstraint('usage_amount >= 0', name='ck_usage_amount_positive'),
    )
