from sqlalchemy import Column, String, VARCHAR, TIMESTAMP, Boolean, ForeignKey, text
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(VARCHAR(50), primary_key=True, index=True)
    hospital_id = Column(VARCHAR(50), ForeignKey("organizations.organization_id"), nullable=False)
    user_name = Column(String(255), nullable=False)
    user_email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    user_role = Column(String(50), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
