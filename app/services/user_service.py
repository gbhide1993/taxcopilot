from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models
from app.models.license import License
from app.utils.security import verify_password
from app.utils.security import get_password_hash




def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def authenticate_user(db, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, user_data):

    license = db.query(License).first()

    if not license or not license.is_active:
        raise HTTPException(status_code=403, detail="License inactive")

    current_user_count = db.query(models.User).count()

    if current_user_count >= license.max_users:
        raise HTTPException(
            status_code=403,
            detail="User limit exceeded for this license"
        )

    # prevent duplicate email
    existing = get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role_id=user_data.role_id,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
