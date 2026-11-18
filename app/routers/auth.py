
# 1. Import Libraries
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, models, utils, oauth2

# 2. Initialize Authentication Router
router = APIRouter(tags=["Authentication"])

# 3. POST - Login and Generate JWT
@router.post("/login")
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    # Find User by Email
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username
    ).first()

    # Validate Email
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verify Hashed Password
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Generate JWT Access Token
    access_token = oauth2.create_access_token(
        data={"user_id": str(user.id)}
    )

    # Return Token
    return {"access_token": access_token, "token_type": "bearer"}
