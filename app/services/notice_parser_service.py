import re
from datetime import datetime




def extract_section(text: str, valid_sections: set[str] = None):

    """
    Production-grade section extraction.

    valid_sections: set of section references from SectionsMaster
                    e.g. {"143", "143(2)", "148", "271(1)(c)"}
    """

    if not text:
        return None

    text = text.replace("\n", " ")

    # -----------------------------------------
    # Layer 1: High-confidence keyword-based
    # -----------------------------------------

    keyword_pattern = re.compile(
        r"(?:u/s|under section|section|r\.?w\.?s\.?)\s*(\d+[A-Za-z]?(?:\(\d+\))*)",
        re.IGNORECASE
    )

    matches = keyword_pattern.findall(text)

    for match in matches:
        candidate = match.strip()
        if valid_sections:
            if candidate in valid_sections:
                return candidate
        else:
            return candidate  # fallback if no validation provided

    # -----------------------------------------
    # Layer 2: Header-only scan
    # -----------------------------------------

    header_text = text[:1000]

    header_pattern = re.compile(
        r"\b\d{2,3}[A-Za-z]?(?:\(\d+\))*\b"
    )

    header_matches = header_pattern.findall(header_text)

    for candidate in header_matches:
        if valid_sections and candidate in valid_sections:
            return candidate

    # -----------------------------------------
    # Layer 3: Full document validated scan
    # -----------------------------------------

    full_matches = header_pattern.findall(text)

    for candidate in full_matches:
        if valid_sections and candidate in valid_sections:
            return candidate

    # -----------------------------------------
    # Nothing reliable found
    # -----------------------------------------

    return None


def extract_assessment_year(text: str):
    match = re.search(r"(?:Assessment Year|AY)\s*[:\-]?\s*(\d{4}\-\d{2})", text, re.IGNORECASE)
    return match.group(1) if match else None


def extract_dates(text: str):
    date_patterns = [
        r"(\d{2}[/-]\d{2}[/-]\d{4})",
        r"(\d{4}[/-]\d{2}[/-]\d{2})"
    ]

    found_dates = []

    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            try:
                parsed = datetime.strptime(m.replace("-", "/"), "%d/%m/%Y")
                found_dates.append(parsed.date())
            except:
                try:
                    parsed = datetime.strptime(m.replace("-", "/"), "%Y/%m/%d")
                    found_dates.append(parsed.date())
                except:
                    continue

    if len(found_dates) >= 2:
        return found_dates[0], found_dates[1]

    return None, None
