from sqlalchemy import Column, String, VARCHAR, TIMESTAMP, func
from app.database import Base


class Organization(Base):
    __tablename__ = "organizations"
    
    organization_id = Column(VARCHAR(50), primary_key=True)
    organization_name = Column(VARCHAR(255), nullable=False)
    organization_type = Column(VARCHAR(50), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
