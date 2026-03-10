import sys
from app.database import SessionLocal
from app.services.section_seed_service import seed_sections


def main():
    if len(sys.argv) < 2:
        print("Usage: python seed_sections.py <path_to_json>")
        sys.exit(1)

    db = SessionLocal()

    result = seed_sections(db, sys.argv[1])

    db.close()

    print("---- Ingestion Summary ----")
    print(f"Inserted: {result['inserted']}")
    print(f"Skipped (duplicates): {result['skipped']}")


if __name__ == "__main__":
    main()
