from typing import List
from Course import Course


class CourseLoad(object):
    def __init__(self, courses: List[Course]) -> None:
        self.courses = sorted(courses, key=lambda course: course.start_time)

    def has_overlaps(self):
        for i in range(0, len(self.courses) - 1):
            for j in range(i + 1, len(self.courses)):
                if self.courses[i].overlaps(self.courses[j]):
                    return True
        return False

    def get_minutes_between_classes(self):
        days = "MTWRF"

        courses_on_days = []
        for day in days:
            current_days_courses = []
            for course in self.courses:
                if day in course.days:
                    current_days_courses.append(course)
            courses_on_days.append(current_days_courses)

        total = 0
        for todays_courses in courses_on_days:
            for i in range(0, len(todays_courses) - 1):
                total += todays_courses[i + 1].start_time - \
                    todays_courses[i].end_time

        return total

    def print_courses(self, verbose=False, num_dashes=47):
        print("-" * num_dashes)
        for course in self.courses:
            print(str(course) if verbose else course.short_out())
            print("-" * num_dashes)

    def __str__(self):

        day_size = 15

        # Start showing at 6AM
        start_time = 7 * 60

        # End showing at 10PM
        stop_time = (8 + 12) * 60

        total_minutes_shown = stop_time - start_time

        minute_increments = 30

        out = [[" " for x in range(5 * day_size)]
               for y in range(total_minutes_shown // minute_increments)]

        days_order = "MTWRF"
        for course in self.courses:
            days_indices = [days_order.index(day) for day in course.days]

            offset = (course.start_time - start_time) // minute_increments
            length = (course.end_time - course.start_time) // minute_increments

            num_content_rows = length - 2
            num_content_columns = day_size - 2

            for index in days_indices:
                starting_index = (day_size - len(course.id)) // 2
                for i, letter in enumerate(course.id):
                    out[offset + 1][index * day_size + starting_index + i] = letter


                out[offset][index * day_size] = "╔"
                out[offset+length][index * day_size] = "╚"
                for dx in range(1, day_size - 1):
                    out[offset][index * day_size + dx] = "═"
                    out[offset + length][index * day_size + dx] = "═"
                out[offset][(index + 1) * day_size - 1] = "╗"
                out[offset+length][(index + 1) * day_size - 1] = "╝"
                for dy in range(1, length):
                    out[offset + dy][index * day_size] = "║"
                    out[offset + dy][(index + 1) * day_size - 1] = "║"

        hour_space_padding = 9

        spaced_days = [" "*((day_size-1)//2) + day + " " *
                       ((day_size)//2) for day in days_order]
        to_return = "\n\n"
        to_return += (" " * hour_space_padding)
        to_return += "".join(spaced_days)
        to_return += "\n"

        for i, row in enumerate(out):
            hour = (((i * minute_increments // 60) +
                    (start_time // 60) - 1) % 12) + 1
            hour_str = "{0:4}".format(hour) + "  "
            pre = (hour_str if (i % (60 // minute_increments) == 0)
                   else " " * 6) + "│  "
            to_return += pre + "".join(row) + "\n"

        return to_return
