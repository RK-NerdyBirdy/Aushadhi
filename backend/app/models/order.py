from sqlalchemy import Column, Integer, String, VARCHAR, NUMERIC, Date, ForeignKey, CheckConstraint, DateTime, func, ForeignKeyConstraint
from app.database import Base

class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    hospital_id = Column(VARCHAR(50), ForeignKey("organizations.organization_id"), nullable=False)
    medicine_id = Column(VARCHAR(50), nullable=False)
    medicine_name = Column(String(255), nullable=False)
    medicine_quantity_predicted = Column(Integer, nullable=False)
    recieved_quantity = Column(Integer, nullable=True)
    expected_delivery_date = Column(Date, nullable=False)
    actual_delivery_date = Column(Date, nullable=True)
    order_status = Column(String(50), nullable=False)
    medicine_price = Column(NUMERIC(12, 2), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    __table_args__ = (
        CheckConstraint('medicine_quantity_predicted >= 0'),
        CheckConstraint('recieved_quantity >= 0'),
        ForeignKeyConstraint(['hospital_id', 'medicine_id'], ['medicine_info.hospital_id', 'medicine_info.medicine_id']),
    )
