import json
import argparse
import sys
import os
from datetime import datetime
from itertools import product
from collections import defaultdict

# Try to import rich; exit gracefully if not installed
try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    from rich.panel import Panel
    from rich.text import Text
    from rich.style import Style
    from rich.align import Align
except ImportError:
    print("This tool requires the 'rich' library for visuals.")
    print("Please run: pip install rich")
    sys.exit(1)

# --- Configuration & Constants ---

DATE_FMT = "%I:%M%p"  # Matches "11:15AM"
DAYS_ORDER = [
    "M",
    "T",
    "W",
    "R",
    "F",
]
DAY_NAMES = {
    "M": "Mon",
    "T": "Tue",
    "W": "Wed",
    "R": "Thu",
    "F": "Fri",
}

# Map shorthand user inputs to the JSON data strings
MODALITY_MAP = {
    "f2f": "Face-to-Face Instruction",
    "hybrid": "Hybrid (F2F & Online Instruc.)",
    "sync": "Online with Synchronous Mtgs.",
    "async": "Online: Asynchronous",
}

# Distinct colors for different courses
COURSE_COLORS = [
    "cyan",
    "magenta",
    "green",
    "yellow",
    "blue",
    "red",
    "bright_white",
]

# Grid Configuration
GRID_START_HOUR = 8  # 8 AM
GRID_END_HOUR = 20  # 8 PM
GRID_INTERVAL = 15  # Minutes
START_MINS = GRID_START_HOUR * 60
END_MINS = GRID_END_HOUR * 60
TOTAL_SLOTS = (END_MINS - START_MINS) // GRID_INTERVAL

console = Console()

# --- Helper Functions ---


def parse_time(time_str):
    """Converts '11:15AM' to minutes from midnight."""
    dt = datetime.strptime(time_str, DATE_FMT)
    return dt.hour * 60 + dt.minute


def minutes_to_str(minutes):
    """Converts minutes back to compact '8:15' or '13:45' format."""
    h = minutes // 60
    m = minutes % 60
    # Using 24h format internally for the grid labels looks cleaner
    return f"{h:02d}:{m:02d}"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


class CourseSection:
    def __init__(self, data, color_idx):
        self.crn = data["crn"]
        self.course = data["course"]
        self.title = data["title"]
        self.modality = data["modality"]
        self.color_name = COURSE_COLORS[color_idx % len(COURSE_COLORS)]
        # Create the style used for background filling
        self.fill_style = Style(bgcolor=self.color_name)
        self.timings = []
        self.is_arranged = True

        if "timing" in data and data["timing"]:
            for t in data["timing"]:
                is_arr_marker = False
                for fld in ("day", "begin", "end"):
                    val = t.get(fld, "")
                    if isinstance(val, str) and "ARR" in val.upper():
                        is_arr_marker = True
                        break

                if is_arr_marker:
                    continue

                self.is_arranged = False
                self.timings.append(
                    {
                        "day": t["day"],
                        "start": parse_time(t["begin"]),
                        "end": parse_time(t["end"]),
                        "location": t.get("location", "Unknown"),
                        "str_times": f"{t['begin']}-{t['end']}",
                    }
                )

    def __repr__(self):
        return f"[{self.course}]"


# --- Logic: Conflicts & Scoring ---


def has_conflict(schedule):
    day_map = defaultdict(list)
    for section in schedule:
        for t in section.timings:
            day_map[t["day"]].append((t["start"], t["end"]))

    for day, slots in day_map.items():
        slots.sort(key=lambda x: x[0])
        for i in range(len(slots) - 1):
            # If current ends after next starts -> Conflict
            if slots[i][1] > slots[i + 1][0]:
                return True
    return False


def calculate_campus_time(schedule):
    day_stats = {}
    for section in schedule:
        for t in section.timings:
            day = t["day"]
            if day not in day_stats:
                day_stats[day] = {"min": float("inf"), "max": float("-inf")}
            day_stats[day]["min"] = min(day_stats[day]["min"], t["start"])
            day_stats[day]["max"] = max(day_stats[day]["max"], t["end"])

    total_minutes = 0
    for day in day_stats:
        total_minutes += day_stats[day]["max"] - day_stats[day]["min"]
    return total_minutes


def meets_constraints(section, earliest, latest, allowed_modalities):
    # If this section is ARRANGED (no explicit meeting times), treat it
    # as compatible with any modality/time constraints — the user asked to
    # assume ARR items won't conflict and should be included.
    if allowed_modalities and not section.is_arranged and section.modality not in allowed_modalities:
        return False
    for t in section.timings:
        if earliest and t["start"] < earliest:
            return False
        if latest and t["end"] > latest:
            return False
    return True


# --- Visualization (The "Rich" Part) ---


def get_slot_index(time_mins):
    """Maps a minute value to the nearest downward 15-minute grid slot index."""
    if time_mins < START_MINS:
        return 0
    if time_mins >= END_MINS:
        return TOTAL_SLOTS - 1
    return (time_mins - START_MINS) // GRID_INTERVAL


def render_schedule(schedule_obj, index, total):
    sections = schedule_obj["sections"]
    score = schedule_obj["score"]

    # 1. Header
    hours = score // 60
    mins = score % 60
    header = Panel(
        Align.center(
            Text(f"Schedule Option {index + 1} of {total}\n", style="bold white on blue")
            + Text(f"Total Campus Burden: {hours}h {mins}m", style="italic grey85 on blue")
        ),
        box=box.ROUNDED,
        style="on blue",
    )

    # 2. Build the 15-Minute Grid System

    # Initialize grid with empty spaces.
    # grid_data[slot_index][day_index]
    # Using 6 spaces to ensure the cell has width even when empty
    empty_cell = Text("      ")
    grid_data = [[empty_cell for _ in range(5)] for _ in range(TOTAL_SLOTS)]

    arr_courses = []

    # Populate the grid data
    for section in sections:
        if section.is_arranged:
            arr_courses.append(section)
            continue

        # Create the solid color block text
        # Using spaces with a background color style
        color_block = Text("      ", style=section.fill_style)

        for t in section.timings:
            if t["day"] not in DAYS_ORDER:
                continue

            day_idx = DAYS_ORDER.index(t["day"])

            # Calculate start and end slots.
            # End slot: subtracting 1 minute ensures that a class ending at 10:15
            # does not occupy the 10:15-10:30 slot.
            start_slot = get_slot_index(t["start"])
            end_slot = get_slot_index(t["end"] - 1)

            for i in range(start_slot, end_slot + 1):
                grid_data[i][day_idx] = color_block

    # 3. Construct the Rich Table
    # Using box.SIMPLE_HEAVY for thicker outer borders, but minimalist inner lines
    table = Table(box=box.SIMPLE_HEAVY, show_lines=False, header_style="bold", padding=(0, 0))
    table.add_column("Time", style="dim", width=6, justify="right")
    for day in DAYS_ORDER:
        table.add_column(DAY_NAMES[day], justify="center", width=8)

    curr_time = START_MINS
    for row_idx, row_content in enumerate(grid_data):
        # Only label hours to reduce noise, or label everything for precision. Let's try labelling everything subtly.
        time_label = minutes_to_str(curr_time)

        # Add styling to make the hour markers stand out slightly more than 15/30/45 markers
        if curr_time % 60 == 0:
            time_label = Text(time_label, style="bold white")
        else:
            time_label = Text(time_label, style="dim grey50")

        table.add_row(time_label, *row_content)
        curr_time += GRID_INTERVAL

    # 4. Legend and Details Panel
    legend_items = []
    for s in sections:
        # Create a small color swatch
        swatch = Text("  ", style=s.fill_style)

        details = Text(f" {s.course} ({s.crn})", style="bold " + s.color_name)
        details.append(f" | {s.title}\n", style="dim")

        if s.is_arranged:
            details.append("   -> Arranged / Online Async\n", style="italic grey70")
        else:
            for t in s.timings:
                details.append(f"   -> {t['day']} {t['str_times']} @ {t['location']}\n", style="grey70")

        legend_items.append(Text.assemble(swatch, details))

    legend_panel = Panel(
        Align.left(Text("\n").join(legend_items)), title="Course Legend & Details", border_style="blue", box=box.ROUNDED
    )

    # 5. Render Layout
    clear_screen()
    console.print(header)
    console.print(table, justify="center")
    console.print(legend_panel)
    console.print(
        Align.center(
            "[bold]Controls:[/bold] [green]N[/green] (Next) | [green]P[/green] (Prev) | [yellow]Goto #[/yellow] | [red]Q[/red] (Quit)"
        ),
        style="on grey15",
    )


# --- Main ---


def main():
    parser = argparse.ArgumentParser(description="Visual University Schedule Generator")
    parser.add_argument("courses", nargs="+", help="List of Course IDs")
    parser.add_argument("--file", default="courses.json", help="Path to JSON file")
    parser.add_argument("--earliest", help="Earliest start time (e.g. 08:00AM)")
    parser.add_argument("--latest", help="Latest end time (e.g. 05:00PM)")
    parser.add_argument("--mode", help="Modalities: f2f, hybrid, sync, async (comma separated)")

    args = parser.parse_args()

    # 1. Load Data
    try:
        with open(args.file, "r") as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Could not find {args.file}")
        sys.exit(1)

    # 2. Parse Constraints
    earliest_min = parse_time(args.earliest) if args.earliest else None
    latest_min = parse_time(args.latest) if args.latest else None

    allowed_modes = []
    if args.mode:
        for m in args.mode.split(","):
            if m.lower() in MODALITY_MAP:
                allowed_modes.append(MODALITY_MAP[m.lower()])
            else:
                console.print(f"[yellow]Warning:[/yellow] Unknown mode '{m}'. Options: f2f, hybrid, sync, async")

    # 3. Organize Valid Sections
    course_buckets = defaultdict(list)
    unique_courses = list(set(args.courses))

    # Assign colors to requested courses stably
    course_color_map = {code: i for i, code in enumerate(unique_courses)}

    for entry in raw_data:
        if entry["course"] in unique_courses:
            section = CourseSection(entry, course_color_map[entry["course"]])
            if meets_constraints(section, earliest_min, latest_min, allowed_modes):
                course_buckets[entry["course"]].append(section)

    # Validation
    for requested in unique_courses:
        if not course_buckets[requested]:
            console.print(
                f"[bold red]Error:[/bold red] No valid sections found for '{requested}' matching constraints."
            )
            sys.exit(1)

    sections_lists = [course_buckets[c] for c in unique_courses]

    # 4. Generate Schedules
    console.print(f"[yellow]Generating schedules for: {', '.join(unique_courses)}...[/yellow]")
    valid_schedules = []

    for schedule_tuple in product(*sections_lists):
        if not has_conflict(schedule_tuple):
            score = calculate_campus_time(schedule_tuple)
            valid_schedules.append({"score": score, "sections": schedule_tuple})

    if not valid_schedules:
        console.print("[bold red]No valid schedules found that meet all constraints.[/bold red]")
        sys.exit(0)

    # Sort: Lowest score first
    valid_schedules.sort(key=lambda x: x["score"])

    # 5. Interactive Loop
    current_idx = 0
    total_scheds = len(valid_schedules)

    while True:
        render_schedule(valid_schedules[current_idx], current_idx, total_scheds)
        user_input = input(">> ").strip().lower()

        if user_input == "q":
            break
        elif user_input == "n":
            if current_idx < total_scheds - 1:
                current_idx += 1
        elif user_input == "p":
            if current_idx > 0:
                current_idx -= 1
        elif user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < total_scheds:
                current_idx = idx


if __name__ == "__main__":
    main()
