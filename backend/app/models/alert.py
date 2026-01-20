from sqlalchemy import Column, Integer, String, VARCHAR, Text, ForeignKey, DateTime, func, ForeignKeyConstraint
from app.database import Base

class Alert(Base):
    __tablename__ = "alerts"
    
    alert_id = Column(Integer, primary_key=True, autoincrement=True)
    hospital_id = Column(VARCHAR(50), ForeignKey("organizations.organization_id"), nullable=False)
    medicine_id = Column(VARCHAR(50), nullable=True)
    alert_type = Column(String(50), nullable=False)
    alert_message = Column(Text, nullable=False)
    alert_status = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        ForeignKeyConstraint(['hospital_id', 'medicine_id'], ['medicine_info.hospital_id', 'medicine_info.medicine_id'], name='fk_alert_medicine'),
    )
