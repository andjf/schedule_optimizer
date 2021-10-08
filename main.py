from iter import get_all_possibilities_iter
from Course import Course
from CourseLoad import CourseLoad
import os
import json


# Define how to clear the screen (Windows)
def clear():
    os.system("cls")

if __name__ == "__main__":
    main()

def main():
    # Open and store course info
    with open('course_data.json') as f:
        data = json.load(f)

    # The courses that the user would like to take
    desired_courses = [
        "MATH-3134",
        "CS-2506",
        "CS-3114",
        "ENGL-3764",
        "STAT-4705",
        "HIST-1115"
    ]


    # Get collection of courses for each desired course
    courses = [[Course(info) for info in sections]
               for sections in data.values() if sections[0]["id"] in desired_courses]

    # Transform courses in to non-overlapping course loads
    course_loads = []
    for selected_courses in get_all_possibilities_iter(courses):
        curr = CourseLoad(selected_courses)
        if not curr.has_overlaps():
            course_loads.append(curr)

    # Sort courses based on the gaps between classes
    course_loads.sort(key=lambda cl: cl.get_minutes_between_classes())

    # Words that would trigger exiting viewing
    exit_words = ["no", "n", "q", "quit", "exit"]

    # Loop through all possible course loads
    i = 0
    while i < len(course_loads):
        # Get current course load
        cl = course_loads[i]
        # Clearing screen for next display
        clear()
        # Printing next possibility
        print(cl)
        # Print basic course info
        cl.print_courses()
        # Check if the user wants to see the next element
        response = input(f"next {i + 1}/{len(course_loads)}? ").lower()
        if response in exit_words:
            # Exit the viewing
            break
        elif "prev" in response:
            # User wants to see the previous course load
            i -= 1
        else:
            # Go to the next course load
            i += 1
