# 1. Importing Libraries
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel

# 2. Initialize FastAPI 
app=FastAPI()

# 3. Define Post Model Using Pydantic
class Post(BaseModel):
    title:str
    content:str
    published:bool=True
    rating:Optional[int]=None

# 4. Create Temporary In-Memory Database
my_posts = [
    {"title":"title of post 1","content":"content of post 1","id":1},
    {"title":"favorite foods","content":"I like pizza","id":2}
]

# 5. Find a Post by ID
def find_post(id):
    for p in my_posts:
        if p["id"]==id:
            return p
    return None

# 6. Find the Index of a Post by ID
def find_index_post(id):
    for i,p in enumerate(my_posts):
        if p["id"]==id:
            return i
    return None

# 7. GET - Root Endpoint
@app.get("/")
def root():
    return {"message":"Hello World"}

# 8. GET - Retrieve All Posts
@app.get("/posts")
def get_posts():
    return {"data":my_posts}

# 9. POST - Create a New Post
@app.post("/posts",status_code=status.HTTP_201_CREATED)
def create_posts(post:Post):
    post_dict = post.model_dump()
    post_dict["id"]=max((p["id"] for p in my_posts),default=0)+1
    my_posts.append(post_dict)
    return {"data":post_dict}

# 10. GET - Retrieve the Latest Post
@app.get("/posts/latest")
def get_latest_post():
    if not my_posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No posts available"
        )
    return {"detail":my_posts[-1]}

# 11. GET - Retrieve a Specific Post by ID
@app.get("/posts/{id}")
def get_post(id:int):
    post=find_post(id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id:{id} was not found"
        )
    return {"post_detail":post}

# 12. DELETE - Remove a Post by ID
@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int):
    index=find_index_post(id)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist"
        )
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# 13. PUT - Update an Existing Post by ID
@app.put("/posts/{id}")
def update_post(id:int,post:Post):
    index=find_index_post(id)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id:{id} does not exist"
        )
    post_dict= post.model_dump()
    post_dict["id"]=id
    my_posts[index]=post_dict
    return {"data":post_dict}