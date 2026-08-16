import re

EMPLOYMENT_TYPE_PATTERNS = {
    "Full-time": [r"\bfull[\s-]?time\b"],
    "Part-time": [r"\bpart[\s-]?time\b"],
    "Contract": [r"\bcontract\b"],
    "Temporary": [r"\btemporary\b", r"\btemp\b"],
    "Other": [r"\bfreelance\b", r"\bgig\b"],
}

EXPERIENCE_PATTERNS = {
    "Internship": [r"\bintern(ship)?\b"],
    "Entry level": [r"\bentry[\s-]?level\b", r"\b0-1 years?\b", r"\bfresher\b"],
    "Associate": [r"\bassociate\b"],
    "Mid-Senior level": [r"\bmid[\s-]?senior\b", r"\b\d\+?\s*years?\b"],
    "Director": [r"\bdirector\b"],
    "Executive": [r"\bexecutive\b", r"\bvp\b", r"\bchief\b"],
}

EDUCATION_PATTERNS = {
    "Bachelor's Degree": [r"\bbachelor'?s?\b", r"\bb\.?tech\b", r"\bb\.?sc\b", r"\bb\.?e\.?\b"],
    "Master's Degree": [r"\bmaster'?s?\b", r"\bm\.?tech\b", r"\bm\.?sc\b", r"\bmba\b"],
    "Doctorate": [r"\bph\.?d\b", r"\bdoctorate\b"],
    "High School or equivalent": [r"\bhigh school\b"],
}


def _match_first(patterns: dict, text: str) -> str | None:
    text_lower = text.lower()
    for label, regex_list in patterns.items():
        for pattern in regex_list:
            if re.search(pattern, text_lower):
                return label
    return None


def parse_pasted_posting(raw_text: str) -> dict:
    
    raw_text = raw_text.strip()
    if not raw_text:
        return {}

    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    result = {}


    if lines and len(lines[0]) <= 80:
        result["title"] = lines[0]

    employment_type = _match_first(EMPLOYMENT_TYPE_PATTERNS, raw_text)
    if employment_type:
        result["employment_type"] = employment_type

    experience = _match_first(EXPERIENCE_PATTERNS, raw_text)
    if experience:
        result["required_experience"] = experience

    education = _match_first(EDUCATION_PATTERNS, raw_text)
    if education:
        result["required_education"] = education

    # The full pasted text also becomes the description by default —
    # the user can still edit/split it manually afterward.
    result["description"] = raw_text

    return result