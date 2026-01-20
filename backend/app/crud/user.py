from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
import uuid

class CRUDUser:
    def get(self, db: Session, user_id: str):
        return db.query(User).filter(User.user_id == user_id).first()
    
    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.user_email == email).first()
    
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()
    
    def get_by_hospital(self, db: Session, hospital_id: str, *, skip: int = 0, limit: int = 100):
        return db.query(User).filter(
            User.hospital_id == hospital_id
        ).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: UserCreate):
        user_id = str(uuid.uuid4())
        db_obj = User(
            user_id=user_id,
            hospital_id=obj_in.hospital_id,
            user_name=obj_in.user_name,
            user_email=obj_in.user_email,
            hashed_password=get_password_hash(obj_in.password),
            user_role=obj_in.user_role,
            is_active=True
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, user_id: str, obj_in: UserUpdate):
        db_obj = self.get(db, user_id)
        if db_obj:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def deactivate(self, db: Session, user_id: str):
        db_obj = self.get(db, user_id)
        if db_obj:
            db_obj.is_active = False
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, user_id: str):
        db_obj = self.get(db, user_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

user = CRUDUser()
