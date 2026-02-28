from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.user_service import authenticate_user
from app.utils.jwt import create_access_token

router = APIRouter()


@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        data={"sub": user.email}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
