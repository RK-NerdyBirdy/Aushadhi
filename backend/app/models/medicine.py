from sqlalchemy import Column, String, VARCHAR, NUMERIC, Boolean, ForeignKey, Text, PrimaryKeyConstraint
from app.database import Base

class MedicineInfo(Base):
    __tablename__ = "medicine_info"
    
    hospital_id = Column(VARCHAR(50), ForeignKey("organizations.organization_id"), nullable=False)
    medicine_id = Column(VARCHAR(50), nullable=False)
    medicine_name = Column(String(255), nullable=False)
    medicine_price = Column(NUMERIC(12, 2), nullable=False)
    cold_storage = Column(Boolean, nullable=False)
    abc_category = Column(String(1), nullable=True)
    ved_category = Column(String(1), nullable=True)
    salt_composition = Column(Text, nullable=True)
    pack_size = Column(String(50), nullable=True)
    
    __table_args__ = (
        PrimaryKeyConstraint('hospital_id', 'medicine_id'),
    )
