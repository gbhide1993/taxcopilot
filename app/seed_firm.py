from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.firm import Firm


def seed_firm():
    db = SessionLocal()

    existing = db.query(Firm).first()

    if existing:
        print("Firm already exists.")
        return

    firm = Firm(
        name="Demo CA Firm",
        license_type="TRIAL",
        trial_expiry=datetime.utcnow() + timedelta(days=30),
        max_users=5,
        max_ai_queries_per_month=100,
        is_active=True
    )

    db.add(firm)
    db.commit()
    db.close()

    print("Firm seeded successfully.")


if __name__ == "__main__":
    seed_firm()
