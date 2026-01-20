from sqlalchemy import TIMESTAMP, Column, Integer, VARCHAR, Numeric, DATE, ForeignKey, CheckConstraint,func
from app.database import Base


class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True)
    hospital_id = Column(VARCHAR(50), ForeignKey("organizations.organization_id"), nullable=False)
    medicine_id = Column(VARCHAR(50), nullable=False)
    medicine_name = Column(VARCHAR(255), nullable=False)
    medicine_quantity_predicted = Column(Integer, nullable=False)
    recieved_quantity = Column(Integer)
    expected_delivery_date = Column(DATE, nullable=False)
    actual_delivery_date = Column(DATE)
    order_status = Column(VARCHAR(50), nullable=False)
    medicine_price = Column(Numeric(12, 2), nullable=False)
    
    __table_args__ = (
        CheckConstraint('medicine_quantity_predicted >= 0', name='ck_order_quantity_positive'),
        CheckConstraint('recieved_quantity >= 0', name='ck_received_quantity_positive'),
    )
