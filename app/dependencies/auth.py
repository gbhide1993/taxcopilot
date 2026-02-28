from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.utils.jwt import verify_token
from app.services.user_service import get_user_by_email
from app.models.user import User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    email = payload.get("sub")
    user = (db.query(User)
        .options(joinedload(User.role))
        .filter(User.email == email)
        .first()
    )
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
