import csv
import ast
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.sections_master import SectionsMaster  # adjust import if needed


CSV_PATH = "sections_master_final_seed_ready.csv"


def seed_sections(truncate=False):
    db: Session = SessionLocal()

    if truncate:
        print("Truncating existing sections_master table...")
        db.query(SectionsMaster).delete()
        db.commit()

    inserted = 0
    skipped = 0

    with open(CSV_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # Convert annexure_template string → list
            annexure = row.get("annexure_template")
            if annexure:
                try:
                    annexure = ast.literal_eval(annexure)
                except Exception:
                    annexure = []
            else:
                annexure = []

            existing = (
                db.query(SectionsMaster)
                .filter(
                    SectionsMaster.act_name == row["act_name"],
                    SectionsMaster.section_reference == row["section_reference"],
                )
                .first()
            )

            if existing:
                skipped += 1
                continue

            section = SectionsMaster(
                act_name=row["act_name"],
                section_reference=row["section_reference"],
                heading=row["Description"],
                category=row["category"],
                workflow_mapping=row["Workflow Mapping"],
                exposure_type=row["exposure_type"] or None,
                severity_level=int(row["severity_level"])
                if row["severity_level"]
                else None,
                penalty_flag=row["penalty_flag"] == "True",
                related_penalty_reference=row["related_penalty_reference"],
                annexure_template=annexure,
            )

            db.add(section)
            inserted += 1

        db.commit()
        db.close()

    print("---- Sections Master Seeding Summary ----")
    print(f"Inserted: {inserted}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    import sys

    truncate_flag = "--truncate" in sys.argv
    seed_sections(truncate=truncate_flag)