from sqlalchemy import Column, String, Boolean
from database import Base


class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    subscribed = Column(Boolean, default=True)
    name = Column(String)