from sqlalchemy import Column, String, VARCHAR, TIMESTAMP, func, Boolean
from app.database import Base


class Organization(Base):
    __tablename__ = "organizations"
    
    organization_id = Column(VARCHAR(50), primary_key=True)
    organization_name = Column(VARCHAR(255), nullable=False)
    organization_type = Column(VARCHAR(50), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    uploaded_files = Column(Boolean, default=False)
    uploaded_time = Column(TIMESTAMP, nullable=True)
