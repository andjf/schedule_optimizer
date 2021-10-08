from typing import List
from iter import get_all_possibilities_iter
from Course import Course
from CourseLoad import CourseLoad
import os
import json


def clear():
    os.system("cls")


with open('course_data.json') as f:
    data = json.load(f)

desired_courses = [
    "CS-3604",
    "CS-3114",
    "CS-3214",
    "CS-2506",
    "CS-3304",
]


courses = [[Course(info) for info in sections]
           for sections in data.values() if sections[0]["id"] in desired_courses]


course_loads = []
for selected_courses in get_all_possibilities_iter(courses):
    curr = CourseLoad(selected_courses)
    if not curr.has_overlaps():
        course_loads.append(curr)

course_loads.sort(key=lambda cl: cl.get_minutes_between_classes())

for i, cl in enumerate(course_loads):
    clear()
    print(cl)
    cl.print_courses()
    if input(f"next {i + 1}/{len(course_loads)}? ").lower() == "no":
        break
