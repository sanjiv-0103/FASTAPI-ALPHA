
# 1. Import Libraries
from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db

# 2. Initialize Router
router = APIRouter()

# 3. GET - Retrieve Posts Using Pagination
@router.get("/posts", response_model=list[schemas.Post])
def get_posts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    posts = db.query(models.Post).order_by(
        models.Post.id
    ).offset(skip).limit(limit).all()
    return posts

# 4. POST - Create Post With Authenticated Owner
@router.post(
    "/posts",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Post
)
def create_posts(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    new_post = models.Post(
        **post.model_dump(),
        owner_id=current_user.id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# 5. GET - Retrieve Latest Post
@router.get("/posts/latest", response_model=schemas.Post)
def get_latest_post(db: Session = Depends(get_db)):
    post = db.query(models.Post).order_by(
        models.Post.id.desc()
    ).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No posts available"
        )

    return post

# 6. GET - Retrieve Post by ID
@router.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(
        models.Post.id == id
    ).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return post

# 7. DELETE - Delete Own Post
@router.delete(
    "/posts/{id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    post = db.query(models.Post).filter(
        models.Post.id == id
    ).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {id} does not exist"
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )

    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# 8. PUT - Update Own Post
@router.put("/posts/{id}", response_model=schemas.Post)
def update_post(
    id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    existing_post = db.query(models.Post).filter(
        models.Post.id == id
    ).first()

    if existing_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {id} does not exist"
        )

    if existing_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )

    for key, value in post.model_dump().items():
        setattr(existing_post, key, value)

    db.commit()
    db.refresh(existing_post)
    return existing_post
