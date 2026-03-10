from app.database import SessionLocal
from app.models.user import User
from app.utils.security import hash_password

def seed_admin():
    db = SessionLocal()

    admin_email = "admin@taxcopilot.local"

    existing_admin = db.query(User).filter(User.email == admin_email).first()

    if not existing_admin:
        admin_user = User(
            email=admin_email,
            full_name="System Admin",
            hashed_password=hash_password("admin123"),
            is_admin=True,
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")

    db.close()

if __name__ == "__main__":
    seed_admin()
