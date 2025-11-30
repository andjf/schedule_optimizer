# Schedule Optimizer

A Python utility to generate and visualize non-conflicting course schedules.

## Setup

First, generate the course data file:

```bash
python ./get_raw_course_data.py
```

This creates `course_data_202601.json` containing all available courses and their sections.

## Usage

Run the schedule optimizer with your desired courses:

```bash
python ./main.py --file ./course_data_202601.json "MATH-3134" "CS-2506" "CS-3114" "ENGL-3764" "STAT-4705" "HIST-1115" --mode f2f
```

### Arguments

- **Courses** (positional): List of course IDs to schedule (e.g., `"CS-1000" "MATH-2000"`)
- **--file**: Path to the course data JSON file (default: `course.json`)
- **--mode**: Filter by modality (comma-separated). Options:
  - `f2f` - Face-to-Face Instruction
  - `hybrid` - Hybrid (F2F & Online)
  - `sync` - Online with Synchronous Meetings
  - `async` - Online: Asynchronous
- **--earliest**: Earliest class start time (e.g., `08:00AM`)
- **--latest**: Latest class end time (e.g., `05:00PM`)

### Interactive Controls

After launching, navigate through generated schedules:
- **N** - Next schedule
- **P** - Previous schedule
- **#** - Jump to schedule number (enter a number)
- **Q** - Quit

## Features

- **Conflict Detection**: Automatically filters out schedules with overlapping classes
- **Campus Time Scoring**: Ranks schedules by total time spent on campus per day
- **Visual Grid**: Color-coded 15-minute grid showing class times across Mon-Fri (8 AM - 8 PM)
- **Course Details**: Displays meeting times, locations, and course information in a legend 4
