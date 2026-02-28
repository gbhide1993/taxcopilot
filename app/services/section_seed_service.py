import json
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.sections_master import SectionsMaster


def validate_section(data: dict):
    required = [
        "act_name",
        "section_reference",
        "heading",
        "full_text",
        "severity_level"
    ]

    for field in required:
        if not data.get(field):
            raise ValueError(f"Missing required field: {field}")

    if not (1 <= int(data["severity_level"]) <= 5):
        raise ValueError("Severity level must be between 1 and 5")


def seed_sections(db: Session, file_path: str):

    with open(file_path, "r", encoding="utf-8") as f:
        sections = json.load(f)

    inserted = 0
    skipped = 0

    for section in sections:
        try:
            validate_section(section)

            stmt = select(SectionsMaster).where(
                SectionsMaster.act_name == section["act_name"],
                SectionsMaster.section_reference == section["section_reference"]
            )

            existing = db.execute(stmt).scalar_one_or_none()

            if existing:
                skipped += 1
                continue

            new_section = SectionsMaster(
                act_name=section["act_name"],
                section_reference=section["section_reference"],
                heading=section["heading"],
                full_text=section["full_text"],
                penalty_flag=section.get("penalty_flag", False),
                severity_level=section["severity_level"],
                annexure_template=section.get("annexure_template")
            )

            db.add(new_section)
            inserted += 1

        except Exception as e:
            print(f"Error inserting section {section.get('section_reference')}: {e}")

    db.commit()

    return {
        "inserted": inserted,
        "skipped": skipped
    }
