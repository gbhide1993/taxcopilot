from sqlalchemy import TIMESTAMP, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime



class Firm(Base):
    __tablename__ = "firms"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    license_type = Column(String)
    trial_expiry = Column(TIMESTAMP)
    max_users = Column(Integer)
    max_ai_queries_per_month = Column(Integer)
    is_active = Column(Boolean)
    created_at = Column(TIMESTAMP)

    # 🔥 NEW BRANDING FIELDS
    address = Column(Text)
    email = Column(String)
    phone = Column(String)
    signature_name = Column(String)
    signature_designation = Column(String)