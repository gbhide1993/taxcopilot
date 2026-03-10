from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user_schema import UserCreate, UserResponse
from app.services.user_service import create_user
from app.dependencies.role_guard import require_role
from app.models.user import User
from app.dependencies.auth import get_current_user
router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse)
def create_new_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["ADMIN"]))
):
    return create_user(db, user)


@router.get("/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(User).all()