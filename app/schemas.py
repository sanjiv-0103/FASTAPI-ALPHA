# 1. Import Libraries
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# 2. Define Common Post Fields
class PostBase(BaseModel):
    title:str
    content:str
    published:bool=True

# 3. Define Schema for Creating Posts
class PostCreate(PostBase):
    pass

# 4. Define Schema for Returning Posts
class Post(PostBase):
    id:int
    created_at:datetime

    model_config=ConfigDict(from_attributes=True)
