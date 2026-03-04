import re
from app.models.sections_master import SectionsMaster


def get_section_by_act_and_number(db, act_name: str, section_reference: str):

    if not act_name or not section_reference:
        return None

    # Normalize incoming section (remove spaces)
    normalized_input = section_reference.strip()

    # Add "Section " prefix for comparison
    formatted_section = f"Section {normalized_input}"

    return db.query(SectionsMaster).filter(
        SectionsMaster.act_name == act_name.strip(),
        SectionsMaster.section_reference == formatted_section
    ).first()