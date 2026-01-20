from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.prediction import HospitalPrediction
from app.schemas.prediction import PredictionCreate, PredictionUpdate

class CRUDPrediction:
    def get(self, db: Session, hospital_id: str, medicine_id: str):
        return db.query(HospitalPrediction).filter(
            and_(
                HospitalPrediction.hospital_id == hospital_id,
                HospitalPrediction.medicine_id == medicine_id
            )
        ).first()
    
    def get_multi(self, db: Session, hospital_id: str, *, skip: int = 0, limit: int = 100):
        return db.query(HospitalPrediction).filter(
            HospitalPrediction.hospital_id == hospital_id
        ).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: PredictionCreate):
        db_obj = HospitalPrediction(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, hospital_id: str, medicine_id: str, obj_in: PredictionUpdate):
        db_obj = self.get(db, hospital_id, medicine_id)
        if db_obj:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, hospital_id: str, medicine_id: str):
        db_obj = self.get(db, hospital_id, medicine_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

prediction = CRUDPrediction()
