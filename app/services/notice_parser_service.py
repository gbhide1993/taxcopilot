import re
from datetime import datetime


def extract_section(text: str):
    match = re.search(r"(?:u/s|under section|section)\s*(\d+[A-Za-z]*)", text, re.IGNORECASE)
    return match.group(1) if match else None


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
