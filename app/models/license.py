from sqlalchemy import Column, Integer, Date, Boolean
from app.database import Base

class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)

    max_users = Column(Integer, default=2)
    expiry_date = Column(Date, nullable=False)

    is_active = Column(Boolean, default=True)
