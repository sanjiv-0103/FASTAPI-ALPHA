
# 1. Import Libraries
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from psycopg2 import Error
from app.database import get_connection

# 2. Initialize FastAPI
app=FastAPI()

# 3. Define Post Model Using Pydantic
class Post(BaseModel):
    title:str
    content:str
    published:bool=True
    rating:Optional[int]=None

# 4. GET - Root Endpoint
@app.get("/")
def root():
    return {"message":"Hello World"}

# 5. GET - Retrieve All Posts From PostgreSQL
@app.get("/posts")
def get_posts():
    conn=get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM posts ORDER BY id")
            posts=cursor.fetchall()
        return {"data":posts}
    finally:
        conn.close()

# 6. POST - Create a New Post in PostgreSQL
@app.post("/posts",status_code=status.HTTP_201_CREATED)
def create_posts(post:Post):
    conn=get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO posts (title,content,published,rating)
                    VALUES (%s,%s,%s,%s)
                    RETURNING *
                    """,
                    (post.title,post.content,post.published,post.rating)
                )
                new_post=cursor.fetchone()
        return {"data":new_post}
    finally:
        conn.close()

# 7. GET - Retrieve the Latest Post
@app.get("/posts/latest")
def get_latest_post():
    conn=get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1")
            post=cursor.fetchone()
        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No posts available"
            )
        return {"detail":post}
    finally:
        conn.close()

# 8. GET - Retrieve a Specific Post by ID
@app.get("/posts/{id}")
def get_post(id:int):
    conn=get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM posts WHERE id=%s",(id,))
            post=cursor.fetchone()
        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id:{id} was not found"
            )
        return {"post_detail":post}
    finally:
        conn.close()

# 9. DELETE - Remove a Post by ID
@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int):
    conn=get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM posts WHERE id=%s RETURNING id",
                    (id,)
                )
                deleted_post=cursor.fetchone()
                if deleted_post is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Post with id:{id} does not exist"
                    )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    finally:
        conn.close()

# 10. PUT - Update an Existing Post by ID
@app.put("/posts/{id}")
def update_post(id:int,post:Post):
    conn=get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE posts
                    SET title=%s,content=%s,published=%s,rating=%s
                    WHERE id=%s
                    RETURNING *
                    """,
                    (post.title,post.content,post.published,post.rating,id)
                )
                updated_post=cursor.fetchone()
                if updated_post is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Post with id:{id} does not exist"
                    )
        return {"data":updated_post}
    finally:
        conn.close()
