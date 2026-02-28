from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class AIQueryLog(Base):
    __tablename__ = "ai_query_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    question = Column(String, nullable=False)

    answer_summary = Column(Text, nullable=True)

    references = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

