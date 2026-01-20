from sqlalchemy import Column, String, VARCHAR, INTEGER, Date, PrimaryKeyConstraint, CheckConstraint, ForeignKeyConstraint
from app.database import Base

class HospitalStock(Base):
    __tablename__ = "hospital_stock"
    
    hospital_id = Column(VARCHAR(50), nullable=False)
    medicine_id = Column(VARCHAR(50), nullable=False)
    medicine_name = Column(String(255), nullable=False)
    medicine_expiry = Column(Date, nullable=False)
    medicine_quantity = Column(INTEGER, nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('hospital_id', 'medicine_id'),
        ForeignKeyConstraint(['hospital_id', 'medicine_id'], ['medicine_info.hospital_id', 'medicine_info.medicine_id']),
        CheckConstraint('medicine_quantity >= 0'),
    )
