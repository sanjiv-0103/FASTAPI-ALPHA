# 1. Import Libraries
from typing import Optional
from fastapi import FastAPI, Depends, Response, status, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import models
from .database import SessionLocal

# 2. Initialize FastAPI
app=FastAPI()

# 3. Define Pydantic Post Model
class Post(BaseModel):
    title:str
    content:str
    published:bool=True
    rating:Optional[int]=None

# 4. Create Database Session Dependency
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. GET - Root Endpoint
@app.get("/")
def root():
    return {"message":"Hello World"}

# 6. GET - Retrieve All Posts Using ORM
@app.get("/posts")
def get_posts(db:Session=Depends(get_db)):
    posts=db.query(models.Post).order_by(models.Post.id).all()
    return {"data":posts}

# 7. POST - Create a New Post Using ORM
@app.post("/posts",status_code=status.HTTP_201_CREATED)
def create_posts(post:Post,db:Session=Depends(get_db)):
    new_post=models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data":new_post}

# 8. GET - Retrieve the Latest Post Using ORM
@app.get("/posts/latest")
def get_latest_post(db:Session=Depends(get_db)):
    post=db.query(models.Post).order_by(models.Post.id.desc()).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No posts available"
        )
    return {"detail":post}

# 9. GET - Retrieve a Specific Post by ID Using ORM
@app.get("/posts/{id}")
def get_post(id:int,db:Session=Depends(get_db)):
    post=db.query(models.Post).filter(models.Post.id==id).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id:{id} was not found"
        )
    return {"post_detail":post}

# 10. DELETE - Remove a Post by ID Using ORM
@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int,db:Session=Depends(get_db)):
    post=db.query(models.Post).filter(models.Post.id==id).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id:{id} does not exist"
        )
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# 11. PUT - Update an Existing Post by ID Using ORM
@app.put("/posts/{id}")
def update_post(id:int,post:Post,db:Session=Depends(get_db)):
    existing_post=db.query(models.Post).filter(models.Post.id==id).first()
    if existing_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id:{id} does not exist"
        )
    post_data=post.model_dump()
    for key,value in post_data.items():
        setattr(existing_post,key,value)
    db.commit()
    db.refresh(existing_post)
    return {"data":existing_post}