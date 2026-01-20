from sqlalchemy import Column, String, VARCHAR, INTEGER, Date, PrimaryKeyConstraint, CheckConstraint, func, ForeignKeyConstraint
from app.database import Base

class HospitalUsage(Base):
    __tablename__ = "hospital_usage"
    
    hospital_id = Column(VARCHAR(50), nullable=False)
    usage_date = Column(Date, nullable=False, server_default=func.current_date())
    medicine_id = Column(VARCHAR(50), nullable=False)
    medicine_name = Column(String(255), nullable=False)
    usage_amount = Column(INTEGER, nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('hospital_id', 'medicine_id'),
        ForeignKeyConstraint(['hospital_id', 'medicine_id'], ['medicine_info.hospital_id', 'medicine_info.medicine_id']),
        CheckConstraint('usage_amount >= 0'),
    )
