from sqlalchemy.orm import Session
from app.models.medicine import MedicineInfo
from app.schemas.medicine import MedicineCreate, MedicineUpdate

class CRUDMedicine:
    def get(self, db: Session, hospital_id: str, medicine_id: str):
        return db.query(MedicineInfo).filter(
            MedicineInfo.hospital_id == hospital_id,
            MedicineInfo.medicine_id == medicine_id
        ).first()
    
    def get_multi(
        self, 
        db: Session, 
        hospital_id: str,
        *,
        skip: int = 0,
        limit: int = 100,
        abc_category: str = None,
        ved_category: str = None,
        cold_storage: bool = None
    ):
        query = db.query(MedicineInfo).filter(MedicineInfo.hospital_id == hospital_id)
        
        if abc_category:
            query = query.filter(MedicineInfo.abc_category == abc_category)
        if ved_category:
            query = query.filter(MedicineInfo.ved_category == ved_category)
        if cold_storage is not None:
            query = query.filter(MedicineInfo.cold_storage == cold_storage)
        
        return query.offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: MedicineCreate):
        db_obj = MedicineInfo(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, hospital_id: str, medicine_id: str, obj_in: MedicineUpdate):
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

medicine = CRUDMedicine()
