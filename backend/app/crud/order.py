from sqlalchemy.orm import Session
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate

class CRUDOrder:
    def get(self, db: Session, order_id: int):
        return db.query(Order).filter(Order.order_id == order_id).first()
    
    def get_multi(self, db: Session, hospital_id: str, *, skip: int = 0, limit: int = 100):
        return db.query(Order).filter(
            Order.hospital_id == hospital_id
        ).offset(skip).limit(limit).all()
    
    def get_by_status(self, db: Session, hospital_id: str, status: str):
        return db.query(Order).filter(
            Order.hospital_id == hospital_id,
            Order.order_status == status
        ).all()
    
    def create(self, db: Session, obj_in: OrderCreate):
        db_obj = Order(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, order_id: int, obj_in: OrderUpdate):
        db_obj = self.get(db, order_id)
        if db_obj:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, order_id: int):
        db_obj = self.get(db, order_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

order = CRUDOrder()
