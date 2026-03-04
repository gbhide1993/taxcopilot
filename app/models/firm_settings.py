from sqlalchemy import Column, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class FirmSettings(Base):
    __tablename__ = "firm_settings"

    id = Column(Integer, primary_key=True, index=True)

    auto_generate_draft = Column(Boolean, default=False)
    auto_generate_risk = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())