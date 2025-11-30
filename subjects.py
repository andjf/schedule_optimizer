import re
from typing import List, Tuple


def extract_subjects_from_html(html_content: str, term: str = "default") -> List[Tuple[str, str]]:
    pattern_prefix = "default" if term == "default" else f'case "{term}"'
    pattern = rf"{pattern_prefix}(.*?)break;"
    match = re.search(pattern, html_content, re.DOTALL)

    if not match:
        return []

    section = match.group(1)

    subject_pattern = r'new Option\("([^"]+)",\s*"([A-Z]+)"'
    matches = re.findall(subject_pattern, section)

    return [(code, name.split(" - ", maxsplit=1)[1]) for name, code in matches]


def get_subjects_from_web(term: str = "default") -> List[Tuple[str, str]]:
    import requests

    HOST = "selfservice.banner.vt.edu"
    RESOURCE = "ssb/HZSKVTSC.P_DispRequest"
    URL = f"https://{HOST}/{RESOURCE}"
    DEFAULT_HEADERS = {
        "Accept": "text/html",
    }

    with requests.Session() as session:
        session.headers.update(DEFAULT_HEADERS)
        response = session.get(URL, timeout=10)
        response.raise_for_status()
        html_content = response.text
        return extract_subjects_from_html(html_content, term=term)
