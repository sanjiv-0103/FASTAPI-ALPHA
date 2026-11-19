
# 1. Import Libraries
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, EmailStr

# 2. Common Post Fields
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

# 3. Schema for Creating Posts
class PostCreate(PostBase):
    pass

# 4. Schema for Returning Posts
class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

# 5. Schema for Creating Users
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# 6. Schema for Returning Users
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# 7. Schema for User Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 8. Schema for JWT Token
class Token(BaseModel):
    access_token: str
    token_type: str

# 9. Schema for Token Data
class TokenData(BaseModel):
    id: Optional[str] = None

# 10. Schema for Voting
class Vote(BaseModel):
    post_id: int
    dir: Literal[0, 1]
