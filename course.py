from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal

DayType = Literal["M", "T", "W", "R", "F", "(ARR)"]


@dataclass
class CourseTiming:
    day: DayType
    begin: str
    end: str
    location: str

    @staticmethod
    def from_day_string(
        day_string: str,
        begin: str,
        end: str,
        location: str,
    ) -> List[CourseTiming]:
        if day_string == "(ARR)":
            return [
                CourseTiming(
                    day="(ARR)",
                    begin=begin,
                    end=end,
                    location=location,
                )
            ]

        return [
            CourseTiming(
                day=char,
                begin=begin,
                end=end,
                location=location,
            )
            for char in day_string
            if char in "MTWRFS"
        ]


@dataclass
class TimetableCourse:
    crn: str
    course: str
    title: str
    schedule_type: str
    modality: str
    credit_hours: str
    capacity: str
    instructor: str
    timing: List[CourseTiming]
    exam: str
    comments: List[str] = field(default_factory=list)

    @staticmethod
    def from_data(
        crn: str,
        course: str,
        title: str,
        schedule_type: str,
        modality: str,
        credit_hours: str,
        capacity: str,
        instructor: str,
        days: str,
        begin: str,
        end: str,
        location: str,
        exam: str,
    ) -> TimetableCourse:
        return TimetableCourse(
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
                begin,
                end,
                location,
            ),
            exam=exam,
        )
    
    def add_comment(self, comment: str) -> None:
        self.comments.append(comment)

    def add_timeing(self, additional_timing: CourseTiming) -> None:
        self.timing.append(additional_timing)
