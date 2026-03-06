from sqlalchemy import Column, Integer, Boolean, DateTime, Float
from sqlalchemy.sql import func
from app.database import Base


class FirmSettings(Base):
    __tablename__ = "firm_settings"

    id = Column(Integer, primary_key=True, index=True)

    auto_generate_draft = Column(Boolean, default=False)
    auto_generate_risk = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


    auto_assign_high_risk = Column(Boolean, default=False)
    high_risk_threshold = Column(Float, default=3.00)