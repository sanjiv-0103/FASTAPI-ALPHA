
# 1. Import Libraries
from fastapi import FastAPI
from .routers import post, user

# 2. Initialize FastAPI
app = FastAPI()

# 3. Include API Routers
app.include_router(post.router)
app.include_router(user.router)

# 4. GET - Root Endpoint
@app.get("/")
def root():
    return {"message": "Hello World"}
