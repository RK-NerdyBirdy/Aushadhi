from sqlalchemy import Column, VARCHAR, Text, Numeric, Boolean, ForeignKey, PrimaryKeyConstraint
from app.database import Base


class MedicineInfo(Base):
    __tablename__ = "medicine_info"
    
    hospital_id = Column(VARCHAR(50), ForeignKey("organizations.organization_id"), nullable=False)
    medicine_id = Column(VARCHAR(50), nullable=False)
    medicine_name = Column(VARCHAR(255), nullable=False)
    medicine_price = Column(Numeric(12, 2), nullable=False)
    cold_storage = Column(Boolean, nullable=False)
    abc_category = Column(VARCHAR(1))
    ved_category = Column(VARCHAR(1))
    salt_composition = Column(VARCHAR(500))
    pack_size = Column(VARCHAR(50))
    
    __table_args__ = (
        PrimaryKeyConstraint('hospital_id', 'medicine_id', name='pk_medicine_info'),
    )
