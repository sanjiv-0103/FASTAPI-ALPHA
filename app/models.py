# 1. Import Libraries
from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

# 2. Define Posts Table
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, default=True)
    rating = Column(Integer, nullable=True)