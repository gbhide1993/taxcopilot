from sqlalchemy import Column, String, Text, Boolean, SmallInteger, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import text
from app.database import Base


class SectionsMaster(Base):
    __tablename__ = "sections_master"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    act_name = Column(Text, nullable=False)
    section_reference = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    heading = Column(Text, nullable=False)
    
    workflow_mapping = Column(String, nullable=True)
    penalty_flag = Column(Boolean, nullable=False, default=False)
    severity_level = Column(SmallInteger, nullable=False, default=1)
    exposure_type = Column(String, nullable=True)
    related_penalty_reference = Column(String, nullable=True)
    annexure_template = Column(JSONB)

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
