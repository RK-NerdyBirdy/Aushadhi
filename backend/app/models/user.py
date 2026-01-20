from sqlalchemy import Column, VARCHAR, TIMESTAMP, Boolean, ForeignKey, func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(VARCHAR(50), primary_key=True)
    hospital_id = Column(VARCHAR(50), ForeignKey("organizations.organization_id"), nullable=False)
    user_name = Column(VARCHAR(255), nullable=False)
    user_email = Column(VARCHAR(255), unique=True, nullable=False)
    user_role = Column(VARCHAR(50), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
