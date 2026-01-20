from sqlalchemy import Column, Integer, VARCHAR, Text, TIMESTAMP, ForeignKey, func
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"
    
    alert_id = Column(Integer, primary_key=True)
    hospital_id = Column(VARCHAR(50), ForeignKey("organizations.organization_id"), nullable=False)
    medicine_id = Column(VARCHAR(50))
    alert_type = Column(VARCHAR(50), nullable=False)
    alert_message = Column(Text, nullable=False)
    alert_status = Column(VARCHAR(50), nullable=False)
    severity = Column(VARCHAR(20))
    created_at = Column(TIMESTAMP, nullable=False, default=func.now())
    resolved_at = Column(TIMESTAMP)
    
    __table_args__ = (
    )
