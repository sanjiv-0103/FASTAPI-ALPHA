# 1. Import Libraries
# 1. Import Libraries
from fastapi import FastAPI, Depends, Response, status, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models, schemas, utils

# Password Hashing Setup
#password_hash = PasswordHash.recommended()

# 2. Initialize FastAPI
app=FastAPI()

# 3. Create Database Session Dependency
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. GET - Root Endpoint
@app.get("/")
def root():
    return {"message":"Hello World"}

# 5. GET - Retrieve All Posts Using ORM
@app.get("/posts",response_model=list[schemas.Post])
def get_posts(db:Session=Depends(get_db)):
    posts=db.query(models.Post).order_by(models.Post.id).all()
    return posts

# 6. POST - Create a New Post Using ORM
@app.post("/posts",status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_posts(post:schemas.PostCreate,db:Session=Depends(get_db)):
    new_post=models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# 7. GET - Retrieve the Latest Post Using ORM
@app.get("/posts/latest",response_model=schemas.Post)
def get_latest_post(db:Session=Depends(get_db)):

    post=db.query(models.Post).order_by(models.Post.id.desc()).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No posts available"
        )
    return post

# 8. GET - Retrieve a Specific Post by ID Using ORM
@app.get("/posts/{id}",response_model=schemas.Post)
def get_post(id:int,db:Session=Depends(get_db)):
    post=db.query(models.Post).filter(models.Post.id==id).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id:{id} was not found"
        )
    return post

# 9. DELETE - Remove a Post by ID Using ORM
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

# 10. PUT - Update an Existing Post by ID Using ORM
@app.put("/posts/{id}",response_model=schemas.Post)
def update_post(id:int,post:schemas.PostCreate,db:Session=Depends(get_db)):
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
    return existing_post


# 11. POST - Register a New User Using ORM
@app.post("/users",status_code=status.HTTP_201_CREATED,response_model=schemas.UserResponse)
def create_user(user:schemas.UserCreate,db:Session=Depends(get_db)):

    # Check Whether Email Already Exists
    existing_user=db.query(models.User).filter(models.User.email==user.email).first()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    # Hash Password Before Saving
    hashed_password=utils.hash(user.password)
    # Create New User
    new_user=models.User(email=user.email,password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/{id}",response_model=schemas.UserResponse)
def get_user(id:int,db:Session=Depends(get_db)):
    user=db.query(models.User).filter(models.User.id==id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id:{id} was not found"
        )
    return user