from sqlalchemy import Column, Integer, String, Boolean
from src.configs.database import Base
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    password = Column(String(60), nullable=True)
    full_name = Column(String(255))
    microsoft_id = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
