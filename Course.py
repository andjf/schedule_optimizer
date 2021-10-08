#!/usr/bin/env python3
# title           :Course.py
# description     :Representation of a course
# author          :Andrew Ferrin
# date            :October 8, 2021
# usage           :from Course import Course; Course(dict)
# python_version  :3.9.2

from typing import Dict


class Course(object):
    """ A class used to represent a Course

    Attributes
    ----------
    `title`: `str`
        The title of the course
    `id`: `str`
        The course subject and number (CS-3114)
    `crn`: `int`
        The course registration number for the course
    `days`: `str`
        The days that this course meets ("MWF" or "TR")
    `meeting_time`: `str`
        The time range that this course meets ("11:00AM-12:15PM")
    `start_time`: `int`
        The number of seconds into the day that this course starts
    `end_time`: `int`
        The number of seconds into the day that this course ends
    `location`: `str`
        The location of the course
    `instructor`: `str`
        The instructor of the course

    Methods
    -------
    `overlaps(other)`: `bool`
        Returns true if this course overlaps with another given course
    `short_out()`: `None`
        Converts this course to a short string 
        (`>> ENGL-3764    MWF 9:05AM-9:55AM       (15020)`)
    """

    def __init__(self, course_info: Dict) -> None:
        """ Creates this course object based on info from a dictionary """
        self.title = course_info["title"]
        self.id = course_info["id"]
        self.crn = course_info["CRN"]
        self.days = course_info["days"]
        self.meeting_time = f"{course_info['start']}-{course_info['end']}"
        self.start_time = Course.__generate_std_time(course_info["start"])
        self.end_time = Course.__generate_std_time(course_info["end"])
        self.location = course_info["location"]
        self.instructor = course_info["instructor"]

    def __shares_day(self, other):
        """ Checks for course overlap by day

        Checks if this course shares a day with another given course

        Parameters
        ----------
        `other`: `Course`
            The other course to check for day overlap with

        Returns
        -------
        `bool`
            `True` if the courses overlap in at least 1 day, `False` otherwise
        """
        return any((day in self.days) for day in other.days)

    def overlaps(self, other) -> bool:
        """ Checks for course overlap

        Checks if this course overlaps with another given course

        Parameters
        ----------
        `other`: `Course`
            The other course to check for overlap with

        Returns
        -------
        `bool`
            `True` if the courses overlap, `False` otherwise
        """
        days_overlap = self.__shares_day(other)
        times_overlap = any(self.start_time <= t <= self.end_time for t in [
                            other.start_time, other.end_time])
        return days_overlap and times_overlap

    def __str__(self) -> str:
        """ To String for Course

        Converts this course to a string

        Returns
        -------
        `str`
            `str` representation of this object
        """
        to_return = "\n" + " " * 15 + self.id + "\n\n"
        to_return += f"Class: {self.title}\n"
        to_return += f"Meeting Time: {self.days} {self.meeting_time}\n"
        to_return += f"Location: {self.location}\n"
        to_return += f"Instructor: {self.instructor} (CRN: {self.crn})"
        return to_return

    def short_out(self) -> str:
        """ Short To String for Course

        Converts this course to a short string
        Ex:
            `>> ENGL-3764    MWF 9:05AM-9:55AM       (15020)`

        Returns
        -------
        `str`
            short `str` representation of this object
        """
        to_return = ">> "
        to_return += self.id
        to_return += f"\t{self.days} {self.meeting_time}\t({self.crn})"
        return to_return

    @staticmethod
    def __generate_std_time(t: str) -> int:
        """ Converts time to standard time

        Converts the given time to the number of minutes into 
        the day that time occurs

        Parameters
        ----------
        `t`: `str`
            The given time.
            Precondition: `t` must be in format `"##:##AM"` or `"#:##PM"` where AM and PM are interchangable

        Returns
        -------
        `int`
            The number of minutes into the day that the given time occurs
        """

        # Gathers the hour
        hour = int(t[0:t.index(":")])

        # Gathers the minute
        minute = int(t[-4:-2])

        # Checks if the time is given in PM or AM
        pm = (t[-2:].upper() == "PM")

        # Accounts for:
        #   - noon (12:00PM => 60 * 12 = 720)
        #   - midnight (12:00AM => 0)
        hour += 12 * ((pm and hour < 12) - (not pm and hour == 12))

        # Returns the total number of minutes into the day
        # that the given time occurs
        return (hour * 60) + minute
