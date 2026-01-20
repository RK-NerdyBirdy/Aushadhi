from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate

class CRUDAlert:
    def get(self, db: Session, alert_id: int):
        return db.query(Alert).filter(Alert.alert_id == alert_id).first()
    
    def get_multi(self, db: Session, hospital_id: str, *, skip: int = 0, limit: int = 100):
        return db.query(Alert).filter(
            Alert.hospital_id == hospital_id
        ).offset(skip).limit(limit).all()
    
    def get_active(self, db: Session, hospital_id: str = None, medicine_id: str = None, alert_type: str = None):
        query = db.query(Alert)
        if hospital_id:
            query = query.filter(Alert.hospital_id == hospital_id)
        query = query.filter(Alert.alert_status == "active")
        if medicine_id:
            query = query.filter(Alert.medicine_id == medicine_id)
        if alert_type:
            query = query.filter(Alert.alert_type == alert_type)
        return query.all()
    
    def get_by_type(self, db: Session, hospital_id: str, alert_type: str):
        return db.query(Alert).filter(
            Alert.hospital_id == hospital_id,
            Alert.alert_type == alert_type
        ).all()
    
    def create(self, db: Session, obj_in: AlertCreate):
        db_obj = Alert(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, alert_id: int, obj_in: AlertUpdate):
        db_obj = self.get(db, alert_id)
        if db_obj:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, alert_id: int):
        db_obj = self.get(db, alert_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

alert = CRUDAlert()
