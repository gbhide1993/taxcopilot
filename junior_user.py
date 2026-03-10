from app.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.user import User
from app.utils.security import hash_password

db = SessionLocal()

junior_role = db.query(Role).filter(Role.name == "JUNIOR_CA").first()

new_user = User(
    email="junior@taxcopilot.local",
    full_name="Junior CA",
    hashed_password=hash_password("password123"),
    role_id=junior_role.id,
    is_active=True
)

db.add(new_user)
db.commit()
db.close()

print("Junior created")
