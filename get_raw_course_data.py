import requests
from bs4 import BeautifulSoup
import json
from typing import List
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict

from course import TimetableCourse, CourseTiming
from subjects import get_subjects_from_web

TERM = "202601"
HOST = "selfservice.banner.vt.edu"
RESOURCE = "ssb/HZSKVTSC.P_ProcRequest"
URL = f"https://{HOST}/{RESOURCE}"
DEFAULT_HEADERS = {
    "Accept": "text/html",
}


def fetch_subject_courses_html(term_year: str, subject_code: str) -> str:
    payload = {
        "CAMPUS": "0",
        "TERMYEAR": term_year,
        "CORE_CODE": "AR%",
        "subj_code": subject_code,
        "SCHDTYPE": "%",
        "CRSE_NUMBER": "",
        "crn": "",
        "open_only": "",
        "disp_comments_in": "Y",
        "sess_code": "%",
        "BTN_PRESSED": "FIND class sections",
        "inst_name": "",
    }

    with requests.Session() as session:
        print(f"Fetching data for subject {subject_code}...")
        session.headers.update(DEFAULT_HEADERS)
        response = session.post(URL, data=payload, timeout=10)
        response.raise_for_status()
        return response.text


def _extract_table_from_html(html_content: str, subject: str):
    """Extract and validate the data table from HTML content."""
    soup = BeautifulSoup(html_content, "html5lib")
    table = soup.find("table", class_="dataentrytable")
    if table is None:
        print(f"No data table found for subject {subject}.")
    return table


def _extract_row_data(row) -> List[str]:
    """Extract text data from a table row."""
    table_data = row.find_all("td")
    return [td.get_text(strip=True) for td in table_data]


def _handle_full_course_row(data: List[str], courses: List[TimetableCourse]) -> None:
    """Handle a row with 13 columns representing a complete course."""
    courses.append(TimetableCourse.from_data(*data))


def _handle_arranged_course_row(data: List[str], courses: List[TimetableCourse]) -> None:
    """Handle a row with 12 columns representing an arranged (ARR) course."""
    (
        crn,
        course,
        title,
        schedule_type,
        modality,
        credit_hours,
        capacity,
        instructor,
        days,
        begin_and_end,
        location,
        exam,
    ) = data
    assert "ARR" in begin_and_end, "Expected ARR for begin and end in arranged course row"
    courses.append(
        TimetableCourse(
            crn=crn,
            course=course,
            title=title,
            schedule_type=schedule_type,
            modality=modality,
            credit_hours=credit_hours,
            capacity=capacity,
            instructor=instructor,
            timing=CourseTiming.from_day_string(
                days,
                "(ARR)",
                "(ARR)",
                location,
            ),
            exam=exam,
        )
    )


def _handle_comment_row(data: List[str], courses: List[TimetableCourse]) -> None:
    """Handle a row containing comments for the last course."""
    assert len(data) == 2, "Unexpected format for comments row"
    courses[-1].add_comment(data[1])


def _handle_additional_times_row(data: List[str], courses: List[TimetableCourse]) -> None:
    """Handle a row with 10 columns representing additional class times."""
    additional_times_literal, days, begin, end, location = data[4:9]
    assert "Additional Times" in additional_times_literal, "Expected '* Additional Times *' in additional times row"
    for current_timing in CourseTiming.from_day_string(days, begin, end, location):
        courses[-1].add_timeing(current_timing)


def _handle_additional_arranged_times_row(data: List[str], courses: List[TimetableCourse]) -> None:
    """Handle a row with 9 columns representing additional arranged class times."""
    additional_times_literal, days, begin_and_end, location = data[4:8]
    assert "Additional Times" in additional_times_literal, "Expected '* Additional Times *' in additional times row"
    assert days == "(ARR)", "Expected (ARR) for days in ARR additional times row"
    assert "ARR" in begin_and_end, "Expected ARR for begin and end in ARR additional times row"
    courses[-1].add_timeing(
        CourseTiming(
            day="(ARR)",
            begin="(ARR)",
            end="(ARR)",
            location=location,
        )
    )


def _process_row(data: List[str], courses: List[TimetableCourse]) -> None:
    """Process a single row of data and add to courses list."""
    try:
        if len(data) == 13:
            _handle_full_course_row(data, courses)
        elif len(data) == 12:
            _handle_arranged_course_row(data, courses)
        elif "Comments for CRN" in data[0]:
            _handle_comment_row(data, courses)
        elif len(data) == 10:
            _handle_additional_times_row(data, courses)
        elif len(data) == 9:
            _handle_additional_arranged_times_row(data, courses)
        else:
            print(f"Skipping row with unexpected number of columns: {data}")
    except AssertionError as e:
        print(f"Error processing row {data}: {e}")
        raise e


def parse_schedule_html(html_content: str, subject: str) -> List[TimetableCourse]:
    """Parse HTML course schedule and extract course information."""
    table = _extract_table_from_html(html_content, subject)
    if table is None:
        print(f"No courses found for subject {subject} (no table). Skipping {subject}.")
        return []
    courses = []
    header_row, *data_rows = table.find_all("tr")
    print(f"Parsing courses for subject {subject}... Found {len(data_rows)} data rows.")
    for row in data_rows:
        data = _extract_row_data(row)
        _process_row(data, courses)

    return courses


def get_all_courses_for_subject(subject_code: str) -> List[TimetableCourse]:
    html_source = fetch_subject_courses_html(TERM, subject_code)
    return parse_schedule_html(html_source, subject_code)


if __name__ == "__main__":
    all_courses = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(
            get_all_courses_for_subject,
            [e[0] for e in get_subjects_from_web(TERM)],
        )
        for course_list in results:
            all_courses.extend(course_list)
    with open(f"course_data_{TERM}.json", "w") as f:
        json.dump([asdict(course) for course in all_courses], f, indent=2)
