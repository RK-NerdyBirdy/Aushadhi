from sqlalchemy import Column, String, VARCHAR, TIMESTAMP, text
from app.database import Base
from datetime import datetime

class Organization(Base):
    __tablename__ = "organizations"
    
    organization_id = Column(VARCHAR(50), primary_key=True, index=True)
    organization_name = Column(String(255), nullable=False)
    organization_type = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
