from sqlalchemy.orm import Session
from src.configs.database import Base
from src.configs.logger import log

class BaseRepository:
    def __init__(self, db: Session, model: Base):
        self.db = db
        self.model = model

    def create(self, obj_in):
        db_obj = self.model(**obj_in.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        log.debug(f"Created {self.model.__name__} with id: {db_obj.id}")
        return db_obj

    def get(self, id: int):
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def update(self, id: int, obj_in):
        db_obj = self.db.query(self.model).filter(self.model.id == id).first()
        if db_obj:
            obj_data = obj_in.dict(exclude_unset=True)
            for key, value in obj_data.items():
                setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int):
        db_obj = self.db.query(self.model).filter(self.model.id == id).first()
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
        return db_obj