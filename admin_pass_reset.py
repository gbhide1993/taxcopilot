from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash

db = SessionLocal()

admin = db.query(User).filter(User.email=="admin@taxcopilot.local").first()

admin.hashed_password = get_password_hash("admin123")

db.commit()
db.close()

print("Admin password reset to admin123")
