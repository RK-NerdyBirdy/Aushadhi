from sqlalchemy import Column, VARCHAR, Integer, DATE, TIMESTAMP, ForeignKey, CheckConstraint, PrimaryKeyConstraint, func
from app.database import Base


class HospitalStock(Base):
    __tablename__ = "hospital_stock"
    
    hospital_id = Column(VARCHAR(50), nullable=False)
    medicine_id = Column(VARCHAR(50), nullable=False)
    medicine_name = Column(VARCHAR(255), nullable=False)
    medicine_expiry = Column(DATE, nullable=False)
    medicine_quantity = Column(Integer, nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('hospital_id', 'medicine_id', name='pk_hospital_stock'),
        CheckConstraint('medicine_quantity >= 0', name='ck_stock_quantity_positive'),
    )
