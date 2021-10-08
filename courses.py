from typing import List
from iter import get_all_possibilities_iter
from Course import Course
from CourseLoad import CourseLoad
import os


def clear():
    os.system("cls")


CS3604 = [
    {
        "id": "CS-3604",
        "title": "Professionalism in Computing",
        "CRN": 13282,
        "days": "TR",
        "start": "11:00AM",
        "end": "12:15PM",
        "location": "PAM 2030",
        "instructor": "DR Dunlap"
    },
    {
        "id": "CS-3604",
        "title": "Professionalism in Computing",
        "CRN": 13283,
        "days": "TR",
        "start": "8:00AM",
        "end": "9:15AM",
        "location": "MCB 113",
        "instructor": "DR Dunlap"
    },
    {
        "id": "CS-3604",
        "title": "Professionalism in Computing",
        "CRN": 13284,
        "days": "MW",
        "start": "2:30PM",
        "end": "3:45PM",
        "location": "ONLINE",
        "instructor": "DR Dunlap"
    }
]

CS3114 = [
    {
        "id": "CS-3114",
        "title": "Data Structures and Algorithms",
        "CRN": 13274,
        "days": "TR",
        "start": "9:30AM",
        "end": "10:45AM",
        "location": "TORG 2150",
        "instructor": "WD McQuain"
    },
    {
        "id": "CS-3114",
        "title": "Data Structures and Algorithms",
        "CRN": 13275,
        "days": "TR",
        "start": "12:30PM",
        "end": "1:45PM",
        "location": "TORG 3100",
        "instructor": "WD McQuain"
    },
    {
        "id": "CS-3114",
        "title": "Data Structures and Algorithms",
        "CRN": 20328,
        "days": "MW",
        "start": "4:00PM",
        "end": "5:15PM",
        "location": "TORG 1060",
        "instructor": "PR Sullivan"
    }
]

CS3214 = [
    {
        "id": "CS-3214",
        "title": "Computer Systems",
        "CRN": 13276,
        "days": "TR",
        "start": "3:30PM",
        "end": "4:45PM",
        "location": "SURGE 104D",
        "instructor": "GV Back"
    },
    {
        "id": "CS-3214",
        "title": "Computer Systems",
        "CRN": 13277,
        "days": "TR",
        "start": "9:30AM",
        "end": "10:45AM",
        "location": "WLH 340",
        "instructor": "DJ Williams"
    },
    {
        "id": "CS-3214",
        "title": "Computer Systems",
        "CRN": 20351,
        "days": "MW",
        "start": "5:30PM",
        "end": "6:45PM",
        "location": "NCB 250",
        "instructor": "L Hu"
    }
]

CS2506 = [
    {
        "id": "CS-2506",
        "title": "Intro to Computer Organization",
        "CRN": 13226,
        "days": "MW",
        "start": "5:30PM",
        "end": "6:45PM",
        "location": "GOODW 190",
        "instructor": "X Jian"
    },
    {
        "id": "CS-2506",
        "title": "Intro to Computer Organization",
        "CRN": 13227,
        "days": "TR",
        "start": "11:00AM",
        "end": "12:15PM",
        "location": "MCB 100",
        "instructor": "DS Nikolopoulos"
    }
]

CS3304 = [
    {
        "id": "CS-3304",
        "title": "Comparative Languages",
        "CRN": 13279,
        "days": "TR",
        "start": "8:00AM",
        "end": "9:15AM",
        "location": "NCB 160",
        "instructor": "MA Gulzar"
    },
    {
        "id": "CS-3304",
        "title": "Comparative Languages",
        "CRN": 13280,
        "days": "TR",
        "start": "5:00PM",
        "end": "6:15PM",
        "location": "NCB 320",
        "instructor": "DP McPherson"
    }
]

classes = [CS3604, CS3114, CS3214, CS2506, CS3304]
courses = [[Course(info) for info in sections] for sections in classes]


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
