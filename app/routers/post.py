
# 1. Import Libraries
from app import oauth2
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db

# 2. Initialize Router
router = APIRouter()

# 3. GET - Retrieve Posts Using Pagination
@router.get("/posts", response_model=list[schemas.Post])
def get_posts(skip:int=0, limit:int=10,db:Session=Depends(get_db)):
    return db.query(models.Post).order_by(models.Post.id).offset(skip).limit(limit).all()

# 4. POST - Create a New Post
@router.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db),get_current_user: schemas.UserResponse = Depends(oauth2.get_current_user)):
    new_post = models.Post(**post.model_dump())
    new_post.user_id = get_current_user.id
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# 5. GET - Retrieve Latest Post
@router.get("/posts/latest", response_model=schemas.Post)
def get_latest_post(db: Session = Depends(get_db)):
    post = db.query(models.Post).order_by(models.Post.id.desc()).first()
    if post is None:
        raise HTTPException(status_code=404, detail="No posts available")
    return post

# 6. GET - Retrieve Post by ID
@router.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


# 7. DELETE - Remove a Post by ID
@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {id} does not exist"
        )

    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)



# 8. PUT - Update an Existing Post
@router.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    existing_post = db.query(models.Post).filter(models.Post.id == id).first()

    if existing_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {id} does not exist"
        )

    for key, value in post.model_dump().items():
        setattr(existing_post, key, value)

    db.commit()
    db.refresh(existing_post)
    return existing_post

