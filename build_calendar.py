#!/usr/bin/env python3
"""Build a Fall 2026 Outlook calendar from the uploaded course syllabi."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Chicago")
UTC = ZoneInfo("UTC")

FIRST = date(2026, 8, 24)
LAST_CLASS = date(2026, 12, 7)
SKIP = {
    date(2026, 9, 7),  # Labor Day
    date(2026, 11, 23),
    date(2026, 11, 24),
    date(2026, 11, 25),
    date(2026, 11, 26),
    date(2026, 11, 27),
    date(2026, 11, 28),
}

# Visible color is the class. Activity is the word in the title, so Outlook
# search can pull every exam or every homework without a second color fighting
# the class color.
CLASS_META = {
    "ARE 102": "🟦",
    "ARE 217": "🟪",
    "CE 311K": "🟧",
    "CE 311S": "🟩",
    "EM 306": "🟥",
    "ME 310T": "🟨",
    "UT Austin": "⬛",
}


def days(start: date, end: date, weekdays: set[int], extra_skip: set[date] | None = None):
    skip = SKIP | (extra_skip or set())
    d = start
    while d <= end:
        if d.weekday() in weekdays and d not in skip:
            yield d
        d += timedelta(days=1)


EVENTS: list[dict] = []


def add(
    day: date,
    summary: str,
    category: str,
    activity: str,
    description: str,
    location: str = "",
    start: time | None = None,
    end: time | None = None,
    busy: bool = True,
    alarms: list[str] | None = None,
    importance: str = "1",
    rrule: str = "",
    exdates: list[date] | None = None,
):
    EVENTS.append(
        {
            "day": day,
            "summary": summary,
            "category": category,
            "activity": activity,
            "description": description.strip(),
            "location": location,
            "start": start,
            "end": end,
            "busy": busy,
            "alarms": alarms or [],
            "importance": importance,
            "rrule": rrule,
            "exdates": exdates or [],
        }
    )


def title(course: str, activity: str, detail: str = "") -> str:
    mark = CLASS_META[course]
    text = f"{mark} {course} · {activity}"
    if detail:
        text += f" · {detail}"
    return text


CLASS_ALARMS = ["-PT15M"]
EXAM_ALARMS = ["-P1D", "-PT2H"]
DUE_ALLDAY_ALARMS = ["-PT15H", "PT9H"]  # 9am the day before, 9am the day of
HW_ALARMS = ["-P1D", "-PT6H"]


WEEKDAY = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]


def series(
    course,
    start_day,
    end_day,
    weekdays,
    activity,
    detail,
    description,
    location,
    start_t,
    end_t,
    busy=True,
    alarms=None,
    importance="1",
    extra_skip=None,
):
    """One repeating event, so Outlook can delete every copy with Delete series."""
    found = list(days(start_day, end_day, weekdays, extra_skip))
    if not found:
        raise RuntimeError(f"no dates for {course} {activity} {detail}")
    first, last = found[0], found[-1]
    found_set = set(found)
    skipped = []
    d = first
    while d <= last:
        if d.weekday() in weekdays and d not in found_set:
            skipped.append(d)
        d += timedelta(days=1)
    byday = ",".join(WEEKDAY[w] for w in sorted(weekdays))
    until = datetime.combine(last, start_t, TZ).astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
    add(
        first,
        title(course, activity, detail),
        course,
        activity,
        description,
        location,
        start_t,
        end_t,
        busy,
        CLASS_ALARMS if alarms is None else alarms,
        importance,
        rrule=f"FREQ=WEEKLY;BYDAY={byday};UNTIL={until}",
        exdates=skipped,
    )


def meeting(
    course,
    day,
    activity,
    detail,
    description,
    location,
    start_t,
    end_t,
    busy=True,
    alarms=None,
    importance="1",
):
    add(
        day,
        title(course, activity, detail),
        course,
        activity,
        description,
        location,
        start_t,
        end_t,
        busy,
        CLASS_ALARMS if alarms is None else alarms,
        importance,
    )


def allday(course, day, activity, detail, description, alarms=None, busy=False, importance="1"):
    add(
        day,
        title(course, activity, detail),
        course,
        activity,
        description,
        "",
        None,
        None,
        busy,
        DUE_ALLDAY_ALARMS if alarms is None else alarms,
        importance,
    )


def block_note(lines: list[str]) -> str:
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# ARE 102
# ---------------------------------------------------------------------------

ARE102_ROOM = "CPE 2.204"
ARE102_LECTURES = [
    (date(2026, 8, 26), "Class introduction", "Atila Novoselac", "", "Lecture",
     "First class. Notebook notes are not required for this meeting."),
    (date(2026, 9, 2), "Architectural design", "Zahid Alibhai", "Ch. 1–3", "Lecture",
     "Read How Buildings Work chapters 1–3 before class."),
    (date(2026, 9, 9), "Residential construction", "Atila Novoselac", "Ch. 4–5", "Lecture",
     "Project 1 details are given after this lecture and in office hours."),
    (date(2026, 9, 16), "Project 1", "Atila Novoselac", "Ch. 6–7", "Lecture",
     "Team project: residential construction and energy-efficiency cost benefits."),
    (date(2026, 9, 23), "Building environmental systems", "Sergio Castellanos", "Ch. 8–9", "Lecture",
     "The syllabus spells the lecturer Segio. Topic dates for guests are tentative."),
    (date(2026, 9, 30), "Construction engineering and project management", "Chriss Rausch", "Ch. 10–11", "Lecture",
     "Guest date is tentative."),
    (date(2026, 10, 7), "Structural and MEP design, path to PE", "James Kleineck and Ansel Early", "Ch. 12", "Lecture",
     "Guest date is tentative."),
    (date(2026, 10, 14), "Exam 1, then indoor environmental quality", "Atila Novoselac", "Ch. 13–14", "Exam",
     "Open-book exam, about 20 minutes, then the lecture continues. Covers readings and lectures from the start of the course through today. Multiple choice or short answer."),
    (date(2026, 10, 21), "The art of structural engineering", "Thomas Taylor, DeSimone", "Ch. 15–16", "Lecture",
     "Guest date is tentative."),
    (date(2026, 10, 28), "Investigation of failures in buildings", "UT ARE forensic-engineering alumni", "Ch. 17", "Lecture",
     "The schedule table labels this day Project 1 due. The Important Dates line instead says October 2. Confirm which date is correct before you rely on either one."),
    (date(2026, 11, 4), "Engineering ethics and professionalism", "John Borcherding", "Ch. 18–19", "Lecture",
     "This lecture is the individual Project 2 topic: ethical and professional responsibilities."),
    (date(2026, 11, 11), "What I wish I knew starting ARE", "Recent ARE graduates", "Ch. 20–21", "Lecture",
     "Guest date is tentative."),
    (date(2026, 11, 18), "Exam 2, then internships and careers", "Atila Novoselac", "Ch. 22", "Exam",
     "Open-book exam, about 20 minutes, then career guidance. Covers readings and lectures after Exam 1."),
    (date(2026, 12, 2), "Internships, careers, and course summary", "Jimmy Canning (ExxonMobil) and Atila Novoselac", "", "Lecture",
     "Last class meeting. Notebook and Project 2 are both listed as due today. Guest speaker dates are tentative."),
]

for day, topic, who, reading, activity, note in ARE102_LECTURES:
    extra = f"\nRead before class: {reading}." if reading else ""
    alarms = EXAM_ALARMS if activity == "Exam" else CLASS_ALARMS
    importance = "2" if activity == "Exam" else "1"
    meeting(
        "ARE 102",
        day,
        activity,
        topic,
        block_note([
            "ARE 102 Introduction to Architectural Engineering",
            "Wednesday class, 2:00–3:00 pm.",
            f"Lecturer: {who}.",
            note,
            "Instructor: Dr. Atila Novoselac, atila@mail.utexas.edu, ECJ 5.430.",
            "TA: Ansel Early, ansel@utexas.edu.",
            "Unique number 17440.",
            "There is no final exam. Two 20-minute exams replace it.",
        ]) + extra,
        ARE102_ROOM,
        time(14, 0),
        time(15, 0),
        alarms=alarms,
        importance=importance,
    )
    if reading:
        allday(
            "ARE 102",
            day,
            "Reading due",
            reading,
            f"Read How Buildings Work {reading} before the 2:00 pm class in {ARE102_ROOM}.",
        )

allday(
    "ARE 102",
    date(2026, 10, 2),
    "Project 1 due",
    "Confirm this date",
    block_note([
        "The Important Dates line says Project 1 is due October 2.",
        "The schedule table instead marks October 28 as Project 1 due.",
        "No clock time is given. Confirm the real deadline with Dr. Novoselac or Canvas before you treat either date as final.",
        "Project 1 is a team project: Residential Construction and Energy Efficiency Cost Benefits Analysis. It is 30% of the grade.",
    ]),
    importance="2",
)
allday(
    "ARE 102",
    date(2026, 10, 28),
    "Project 1 due",
    "Date printed on the schedule",
    block_note([
        "The course schedule labels October 28 as Project 1 due.",
        "The Important Dates line says October 2 instead.",
        "Both dates are on this calendar until you confirm which one Canvas is using.",
        "Project 1 is the team residential-construction and energy-efficiency analysis, worth 30%.",
    ]),
    importance="2",
)
allday(
    "ARE 102",
    date(2026, 10, 16),
    "Checkpoint",
    "Notebook pieces still open",
    block_note([
        "The electronic notebook is due December 2 and is not accepted after December 7.",
        "Still required if you have not done them:",
        "1. A one-page summary of an Architectural Engineering Institute meeting. If AEI is not available, an ASCE, ASHRAE, or other approved UT student-society meeting is allowed after you confirm it with the instructor.",
        "2. A one-page summary of a visit to the Sanger Learning Skills Center.",
        "Lecture notes (half a page to one page) are also required for every lecture except the first and the last.",
    ]),
)
allday(
    "ARE 102",
    date(2026, 12, 2),
    "Project 2 due",
    "Engineering ethics",
    "Individual project on ethical and professional responsibilities. The Important Dates line lists December 2. No clock time is given. Worth 5%.",
    importance="2",
)
allday(
    "ARE 102",
    date(2026, 12, 2),
    "Notebook due",
    "Upload to Canvas",
    block_note([
        "Upload the electronic notebook to Canvas today.",
        "Include lecture notes, the student-society meeting summary, and the Sanger Learning Skills Center summary.",
        "Photos of handwritten notes compiled into a PDF are acceptable.",
        "Late work loses 10% per day.",
    ]),
    importance="2",
)
allday(
    "ARE 102",
    date(2026, 12, 7),
    "Notebook cutoff",
    "No credit after today",
    "Notebooks are not accepted after December 7. This is the hard stop from the syllabus, not a new assignment.",
    importance="2",
)

series(
    "ARE 102",
    date(2026, 8, 25),
    date(2026, 12, 3),
    {1, 3},
    "Office hours",
    "Dr. Novoselac",
    block_note([
        "Tuesday and Thursday, 11:00 am–12:00 pm. Other times by appointment.",
        "Dr. Atila Novoselac, ECJ 5.430, atila@mail.utexas.edu.",
        "This block overlaps ME 310T lecture (Tue/Thu 11:00 am–12:30 pm). Use another time or email for an appointment if you are in both.",
    ]),
    "ECJ 5.430",
    time(11, 0),
    time(12, 0),
    busy=False,
    alarms=[],
)

# ---------------------------------------------------------------------------
# ME 310T
# ---------------------------------------------------------------------------

ME_ROOM = "CMA 2.306"
ME_CLASSES = [
    (date(2026, 8, 25), "Course policy and thermo problems", "Lecture", ""),
    (date(2026, 8, 27), "Otto and Diesel cycles; T, P, energy, work, heat", "Lecture", ""),
    (date(2026, 9, 1), "Energy, work, heat, enthalpy, and entropy", "Lecture", ""),
    (date(2026, 9, 3), "Ideal gas law and specific heats", "Lecture", "HW 1 is due Friday, September 4, at 9:00 pm."),
    (date(2026, 9, 8), "Specific heats and energy or enthalpy change", "Lecture", ""),
    (date(2026, 9, 10), "Entropy change of an ideal gas", "Lecture", "HW 2 is due Friday, September 11, at 9:00 pm."),
    (date(2026, 9, 15), "Isentropic process of an ideal gas", "Quiz", "In-class quiz on HW 2."),
    (date(2026, 9, 17), "First law for a closed system", "Lecture", "HW 3 is due Friday, September 18, at 9:00 pm."),
    (date(2026, 9, 22), "Ideal Otto cycle examples", "Quiz", "In-class quiz on HW 3."),
    (date(2026, 9, 24), "Ideal Diesel cycle examples", "Lecture", "HW 4 is due Friday, September 25, at 9:00 pm."),
    (date(2026, 9, 29), "Otto and Diesel cycle examples", "Quiz", "In-class quiz on HW 4."),
    (date(2026, 10, 1), "Otto and Diesel cycle examples", "Lecture", "HW 5 (Diesel cycle) has no due date. There is no quiz on HW 5."),
    (date(2026, 10, 6), "Review: Otto and Diesel cycles", "Review", "No quiz today."),
    (date(2026, 10, 8), "Exam 1: Otto and Diesel cycles", "Exam", "In class. Closed to the Otto and Diesel module."),
    (date(2026, 10, 13), "Brayton cycles and the first law", "Lecture", ""),
    (date(2026, 10, 15), "First law for open systems; steady processes", "Lecture", "HW 6 is due Friday, October 16, at 9:00 pm."),
    (date(2026, 10, 20), "Brayton cycle examples", "Quiz", "In-class quiz on HW 6."),
    (date(2026, 10, 22), "Brayton cycle examples", "Lecture", "HW 7 is due Friday, October 23, at 9:00 pm."),
    (date(2026, 10, 27), "Heat conduction introduction", "Quiz", "In-class quiz on HW 7. Module 3 starts."),
    (date(2026, 10, 29), "Heat conduction", "Lecture", ""),
    (date(2026, 11, 3), "Heat conduction", "Lecture", ""),
    (date(2026, 11, 5), "Exam 2: Brayton cycle", "Exam", "In class."),
    (date(2026, 11, 10), "Heat convection", "Lecture", ""),
    (date(2026, 11, 12), "Heat convection", "Lecture", "HW 8 is due Friday, November 13, at 9:00 pm."),
    (date(2026, 11, 17), "Radiation", "Quiz", "In-class quiz on HW 8."),
    (date(2026, 11, 19), "Heat exchangers", "Lecture", "HW 9 is due Friday, November 20, at 9:00 pm."),
    (date(2026, 12, 1), "Review and practice exam", "Quiz", "In-class quiz on HW 9."),
    (date(2026, 12, 3), "Review and practice exam", "Review", "HW 10 is due Friday, December 4, at 9:00 pm."),
]

for day, topic, activity, note in ME_CLASSES:
    kind = "Exam" if activity == "Exam" else ("Lecture + Quiz" if activity == "Quiz" else activity)
    meeting(
        "ME 310T",
        day,
        kind,
        topic,
        block_note([
            "ME 310T Applied Thermodynamics, unique 19810.",
            "Tuesday and Thursday, 11:00 am–12:30 pm.",
            "Instructor: Dr. Yaguo Wang, yaguo.wang@austin.utexas.edu.",
            note,
            "Weekly Tuesday quizzes are based on the homework. The syllabus also says the quiz follows the previous Thursday submission; the written deadline rule is Friday at 9:00 pm. If Canvas disagrees, follow Canvas.",
            "Attendance is checked at random and is 5% of the grade.",
        ]),
        ME_ROOM,
        time(11, 0),
        time(12, 30),
        alarms=EXAM_ALARMS if activity == "Exam" else CLASS_ALARMS,
        importance="2" if activity == "Exam" else "1",
    )

ME_HW = [
    (date(2026, 9, 4), date(2026, 9, 6), "HW 1", "Basic thermo properties"),
    (date(2026, 9, 11), date(2026, 9, 13), "HW 2", "Ideal gas"),
    (date(2026, 9, 18), date(2026, 9, 20), "HW 3", "Ideal gas"),
    (date(2026, 9, 25), date(2026, 9, 27), "HW 4", "Otto cycle"),
    (date(2026, 10, 16), date(2026, 10, 18), "HW 6", "First law"),
    (date(2026, 10, 23), date(2026, 10, 25), "HW 7", "Brayton cycle"),
    (date(2026, 11, 13), date(2026, 11, 15), "HW 8", "Conduction"),
    (date(2026, 11, 20), date(2026, 11, 22), "HW 9", "Convection"),
    (date(2026, 12, 4), date(2026, 12, 6), "HW 10", "Radiation and heat exchangers"),
]
for due, fix, name, topic in ME_HW:
    meeting(
        "ME 310T",
        due,
        "HW due",
        f"{name} · {topic} · 9pm",
        block_note([
            f"{name} ({topic}) must be submitted on Canvas before 9:00 pm.",
            "This first submission is required and must be complete. Incomplete work loses credit.",
            "The schedule table places each homework on the Thursday class row. The rule on page 1 says the deadline is Friday at 9:00 pm, which is the time used here.",
            "HW 5 (Diesel cycle) is the missing number and has no due date.",
            "Late homework is not accepted.",
        ]),
        "Canvas",
        time(20, 0),
        time(21, 0),
        busy=False,
        alarms=HW_ALARMS,
        importance="2",
    )
    meeting(
        "ME 310T",
        fix,
        "Optional HW fix",
        f"{name} by midnight",
        block_note([
            f"Optional second submission for {name}.",
            "After solutions are posted, you may correct the homework and submit the update before Sunday midnight.",
            "Do not overwrite the first submission.",
            "If the first submission was complete, the grade is based on this second submission.",
            "If the first submission was incomplete, you still lose some credit.",
        ]),
        "Canvas",
        time(23, 0),
        time(23, 59),
        busy=False,
        alarms=["-PT6H"],
    )

meeting(
    "ME 310T",
    date(2026, 12, 10),
    "Exam",
    "Final · 1–3pm",
    block_note([
        "Thursday, December 10, 1:00–3:00 pm.",
        "The syllabus says this time will be finalized by September 21. Check the registrar schedule that day and move this event if the room or time changes.",
        "Room is not printed in the syllabus.",
        "Final exam is 30% of the grade.",
    ]),
    "Room on the registrar final-exam schedule",
    time(13, 0),
    time(15, 0),
    alarms=EXAM_ALARMS,
    importance="2",
)
allday(
    "ME 310T",
    date(2026, 9, 10),
    "Deadline",
    "SSD letter to Dr. Wang",
    "If you have a disability accommodation letter, discuss it with Dr. Wang before September 10.",
)

series(
    "ME 310T",
    date(2026, 8, 25),
    date(2026, 12, 3),
    {1, 3},
    "Office hours",
    "Dr. Wang · Zoom",
    "Tuesday and Thursday, 3:00–4:00 pm, on Zoom. In-person is by appointment. yaguo.wang@austin.utexas.edu.",
    "Zoom",
    time(15, 0),
    time(16, 0),
    busy=False,
    alarms=[],
)

# Recitations start the second week. Attendance is voluntary.
# 5 points toward a homework, usable twice, until that homework is full credit.
RECITATION_NOTE = (
    "Optional. Recitations start the second week. "
    "You can earn 5 points toward the associated homework by attending any recitation, at most twice, until that homework is already full credit."
)
recitations = [
    ("Sotoudeh", "Zoom", {1}, time(13, 0), time(14, 0), date(2026, 9, 1), date(2026, 12, 1), ""),
    ("Sotoudeh", "ETC 7.111", {2}, time(11, 0), time(12, 0), date(2026, 9, 2), date(2026, 12, 2),
     "Overlaps CE 311S lecture (11:00–11:50 am). Other Sotoudeh times: Tue 1–2 Zoom, Thu 1–2 Zoom, Fri 10:30–11:30 ETC 7.111."),
    ("Sotoudeh", "Zoom", {3}, time(13, 0), time(14, 0), date(2026, 9, 3), date(2026, 12, 3), ""),
    ("Sotoudeh", "ETC 7.111", {4}, time(10, 30), time(11, 30), date(2026, 9, 4), date(2026, 12, 4), ""),
    ("Leang", "ETC 7.111", {0}, time(14, 0), time(15, 0), date(2026, 8, 31), date(2026, 12, 7), ""),
    ("Leang", "Zoom", {2}, time(14, 0), time(15, 0), date(2026, 9, 2), date(2026, 12, 2),
     "Overlaps ARE 102 class (Wed 2:00–3:00 pm). Other Leang times: Mon 2–3 ETC 7.111, Thu 2–3 ETC 7.111, Fri 2–3 Zoom."),
    ("Leang", "ETC 7.111", {3}, time(14, 0), time(15, 0), date(2026, 9, 3), date(2026, 12, 3), ""),
    ("Leang", "Zoom", {4}, time(14, 0), time(15, 0), date(2026, 9, 4), date(2026, 12, 4), ""),
]
for who, where, weekdays, start_t, end_t, start_d, end_d, conflict in recitations:
    series(
        "ME 310T",
        start_d,
        end_d,
        weekdays,
        "Recitation",
        f"{who} · optional",
        block_note([
            RECITATION_NOTE,
            "Freshteh Sotoudeh: f.sotoudeh@utmail.utexas.edu." if who == "Sotoudeh" else "Dalim Leang: dl38734@my.utexas.edu.",
            conflict,
        ]),
        where,
        start_t,
        end_t,
        busy=False,
        alarms=[],
    )

# ---------------------------------------------------------------------------
# CE 311K
# ---------------------------------------------------------------------------

CE311K_ROOM = "RLP 0.102"
series(
    "CE 311K",
    date(2026, 8, 25),
    date(2026, 12, 3),
    {1, 3},
    "Lecture",
    "MATLAB and numerical methods",
    block_note([
        "CE 311K Introduction to Computer Methods.",
        "Tuesday and Thursday, 8:00–9:30 am, RLP 0.102.",
        "The syllabus has a topic outline, not a day-by-day schedule:",
        "1. Introduction to computing, simulations, operating systems, round-off and truncation error.",
        "2. MATLAB: environment, structured programming, arrays, control flow, scripts and functions, graphing, symbolic operations.",
        "3. Numerical methods: error, roots, curve fitting, integration and differentiation, Ax = b, ODEs, finite differences.",
        "Instructor: Dr. Othman Oudghiri-Idrissi, ECJ 4.706, othmanoi@utexas.edu.",
        "Homework and lab due dates are not listed. They are due at 11:59 pm on the Canvas date. You have three penalty-free late days total.",
        "Attendance at lecture and lab is mandatory.",
        "October 13 and November 19 are exams, so this repeating lecture skips those mornings.",
    ]),
    CE311K_ROOM,
    time(8, 0),
    time(9, 30),
    extra_skip={date(2026, 10, 13), date(2026, 11, 19)},
)

meeting(
    "CE 311K",
    date(2026, 10, 13),
    "Exam",
    "Midterm 1",
    block_note([
        "Tuesday, October 13, 8:00–9:15 am, RLP 0.102.",
        "Tentative in the syllabus. Worth 20%.",
        "This replaces the regular 8:00–9:30 lecture.",
        "A makeup is offered only for special circumstances such as a medical reason, and it may be oral or written.",
    ]),
    CE311K_ROOM,
    time(8, 0),
    time(9, 15),
    alarms=EXAM_ALARMS,
    importance="2",
)
meeting(
    "CE 311K",
    date(2026, 11, 19),
    "Exam",
    "Midterm 2",
    block_note([
        "Thursday, November 19.",
        "The syllabus names the day and not the clock time. This event uses the regular class period, 8:00–9:30 am in RLP 0.102.",
        "Move it if Canvas posts a different time or room. Worth 20%. Tentative.",
    ]),
    CE311K_ROOM,
    time(8, 0),
    time(9, 30),
    alarms=EXAM_ALARMS,
    importance="2",
)
meeting(
    "CE 311K",
    date(2026, 12, 11),
    "Exam",
    "Final · 10:30–12:30",
    "Friday, December 11, 10:30 am–12:30 pm. Room is not in the syllabus. Worth 30%.",
    "Room on the registrar final-exam schedule",
    time(10, 30),
    time(12, 30),
    alarms=EXAM_ALARMS,
    importance="2",
)

series(
    "CE 311K", date(2026, 8, 25), date(2026, 12, 3), {1, 3},
    "Office hours", "Dr. Oudghiri",
    "Tuesday and Thursday, 10:00–11:00 am, or by appointment. ECJ 4.706. othmanoi@utexas.edu.",
    "ECJ 4.706", time(10, 0), time(11, 0), busy=False, alarms=[],
)
series(
    "CE 311K", date(2026, 8, 24), LAST_CLASS, {0, 3},
    "Office hours", "TA Khazi",
    "Mohamed Habeebulla Khazi. Monday and Thursday, 3:00–4:00 pm. ECJ 6.406, or a room the TA announces. mhkhazi@utexas.edu.",
    "ECJ 6.406", time(15, 0), time(16, 0), busy=False, alarms=[],
)
series(
    "CE 311K", date(2026, 8, 24), LAST_CLASS, {0, 2},
    "Office hours", "TA Niu",
    block_note([
        "Chi-Wei Niu. Monday and Wednesday, 11:00 am–12:00 pm.",
        "ECJ 6.406, or a room the TA announces. chiweiniu@utexas.edu.",
        "Overlaps CE 311S lecture (11:00–11:50 am).",
    ]),
    "ECJ 6.406", time(11, 0), time(12, 0), busy=False, alarms=[],
)

CE311K_LABS = [
    ("17605", "Fri 12–2", {4}, time(12, 0), time(14, 0), "Friday lab starts at noon, right after CE 311S lecture ends at 11:50. It overlaps Dr. Kockelman's Friday office hours (12:30–2:00)."),
    ("17610", "Fri 2–4", {4}, time(14, 0), time(16, 0), "Overlaps the end of tutor Grotewold's Friday hours (12:00–3:00) and sits next to Dr. Kockelman's Friday office hours."),
    ("17615", "Wed 3–5", {2}, time(15, 0), time(17, 0), "ARE 102 ends at 3:00 pm on Wednesday, so this lab starts as that class ends."),
    ("17620", "Tue 4–6", {1}, time(16, 0), time(18, 0), "Same time as EM 306 discussion #16225 (Tue 4:00–6:00 pm). Do not keep both if you are registered for that discussion."),
]
for unique, label, weekdays, start_t, end_t, note in CE311K_LABS:
    series(
        "CE 311K",
        date(2026, 8, 25),
        date(2026, 12, 4),
        weekdays,
        "Lab",
        f"#{unique} · {label}",
        block_note([
            f"DELETE this whole series if your unique number is not {unique}.",
            "In Outlook, open any one of these and choose Delete series.",
            "CE 311K lab, ECJ 2.210.",
            "Lab assignments are 10% of the grade and are due at 11:59 pm on the posted Canvas date.",
            "The syllabus does not list lab topics by week.",
            note,
        ]),
        "ECJ 2.210",
        start_t,
        end_t,
    )

# ---------------------------------------------------------------------------
# CE 311S lecture + lab
# ---------------------------------------------------------------------------

CE311S_EXAMS = {
    date(2026, 9, 18): ("Exam", "Exam 1", "In class, 11:00–11:50 am. Lessons 1–3: introduction, describing data (Ch. 1), probability (Ch. 2). Worth 9%. Tentative and may move with class progress."),
    date(2026, 10, 9): ("Exam", "Exam 2", "In class, 11:00–11:50 am. After Exam 1 the window is Lessons 4–5: discrete random variables, binomial and Poisson (Ch. 3). Worth 11%."),
    date(2026, 11, 6): ("Exam", "Exam 3", "In class, 11:00–11:50 am. After Exam 2 the window is Lessons 6–8: continuous random variables, gamma and exponential, bivariate and multivariate (Ch. 4–5). Worth 13%."),
    date(2026, 11, 30): ("Exam", "Exam 4", "In class, 11:00–11:50 am. The syllabus capitalizes MONDAY. After Exam 3 the window is Lessons 9–10: distributions of statistics, inference and confidence intervals (Ch. 5 and 7). Worth 14%. Lab 8 is the same afternoon."),
}

def ce311s_window(day: date) -> str:
    if day < date(2026, 9, 18):
        return "Topic window before Exam 1: Lesson 1 Introduction (Ch. 1), Lesson 2 Describing data (Ch. 1, skip boxplots pp. 35–39), Lesson 3 Probability (Ch. 2). The syllabus does not assign a lesson to each date."
    if day < date(2026, 10, 9):
        return "Topic window before Exam 2: Lesson 4 Discrete random variables (Ch. 3), Lesson 5 Binomial and Poisson (skip hypergeometric and negative binomial, pp. 116–121)."
    if day < date(2026, 11, 6):
        return "Topic window before Exam 3: Lesson 6 Continuous random variables (Ch. 4), Lesson 7 Gamma and exponential (skip Weibull, beta, and probability plots, pp. 163–179), Lesson 8 Bivariate and multivariate (Ch. 5)."
    if day < date(2026, 11, 30):
        return "Topic window before Exam 4: Lesson 9 Distributions of statistics (Ch. 5), Lesson 10 Inference and confidence intervals (Ch. 7)."
    return "After Exam 4: Lesson 11 Large and small sample confidence intervals (Ch. 7), Lesson 12 Hypothesis testing (Ch. 8). Lesson 13 linear regression (Ch. 12) is optional. Final exam time is not in the syllabus."


for day in days(FIRST, LAST_CLASS, {0, 2, 4}):
    if day in CE311S_EXAMS:
        activity, detail, note = CE311S_EXAMS[day]
        meeting(
            "CE 311S",
            day,
            activity,
            detail,
            block_note([
                "CE 311S Probability and Statistics for Civil Engineers.",
                "Lecture is Mon/Wed/Fri 11:00–11:50 am in CPE 2.218.",
                note,
                "Make-up exams are not generally given.",
                "Unannounced reading quizzes are possible.",
                "Homework is assigned almost weekly and is due before 10:00 pm. The syllabus does not list those dates. No credit if late. The lowest homework is dropped. Finish every problem within 3 weeks, and at least one week before the final, or participation drops.",
            ]),
            "CPE 2.218",
            time(11, 0),
            time(11, 50),
            alarms=EXAM_ALARMS,
            importance="2",
        )
    else:
        meeting(
            "CE 311S",
            day,
            "Lecture",
            "Probability and statistics",
            block_note([
                "Mon/Wed/Fri 11:00–11:50 am, CPE 2.218.",
                "Professor Kara Kockelman, ECJ 6.904, kkockelm@mail.utexas.edu, office phone 512-471-0210.",
                ce311s_window(day),
                "Homework due dates are not in the syllabus. They are due before 10:00 pm on the assigned day.",
                "Course packet: $30 from IT Printing (Jerome Kubala, 512-497-6662) via Venmo, on a Friday right after class.",
            ]),
            "CPE 2.218",
            time(11, 0),
            time(11, 50),
        )

CE311S_LABS = [
    (date(2026, 8, 24), "Lab 0", "Calculus review", "lab"),
    (date(2026, 8, 31), "Lab 1", "Probability in lifeline design", "lab"),
    (date(2026, 9, 14), "Review", "Exam 1 review", "review"),
    (date(2026, 9, 21), "Lab 2", "Waste containment probabilities", "lab"),
    (date(2026, 9, 28), "Lab 3", "Construction labor costs", "lab"),
    (date(2026, 10, 5), "Review", "Exam 2 review", "review"),
    (date(2026, 10, 12), "Lab 4", "Levee design, normal distribution", "lab"),
    (date(2026, 10, 19), "Lab 5", "Hydraulic conductivity, lognormal", "lab"),
    (date(2026, 10, 26), "Lab 6", "Column reliability", "lab"),
    (date(2026, 11, 2), "Review", "Exam 3 review", "review"),
    (date(2026, 11, 9), "Lab 7", "Mercury emission intervals", "lab"),
    (date(2026, 11, 16), "Review", "Exam 4 review", "review"),
    (date(2026, 11, 30), "Lab 8", "Income regression", "lab"),
    (date(2026, 12, 7), "Review", "Final exam review", "review"),
]
# Lab syllabus "respectively" order. Confirm against your registration.
CE311S_SECTIONS = [
    ("17645", "1–2pm", time(13, 0), time(14, 0), ""),
    ("17655", "2–3pm", time(14, 0), time(15, 0), "Same hour as ARE 102 on Wednesdays only. This lab is Monday, so it does not overlap ARE 102."),
    ("17660", "3–4pm", time(15, 0), time(16, 0), ""),
    ("17650", "4–5pm", time(16, 0), time(17, 0), "Overlaps the first hour of EM 306 discussion #16220 (Mon 4:00–6:00 pm)."),
]
LAB_SCHEDULE = "\n".join(
    f"{day.strftime('%b %-d')}: {activity} — {detail}." for day, activity, detail, _kind in CE311S_LABS
)
for unique, label, start_t, end_t, conflict in CE311S_SECTIONS:
    series(
        "CE 311S",
        FIRST,
        LAST_CLASS,
        {0},
        "Lab",
        f"#{unique} · {label}",
        block_note([
            f"DELETE this whole series if your unique number is not {unique}.",
            "In Outlook, open any one of these and choose Delete series.",
            f"Monday {label}, ECJ 2.218. TA Sadab Khan, sk67837@my.utexas.edu.",
            "The all-day event on each Monday names that week's lab or review.",
            "The lecture syllabus lists unique numbers 17645, 17650, 17655, and 17660. The lab syllabus pairs 17645, 17655, 17660, and 17650 with 1–2, 2–3, 3–4, and 4–5. Confirm your registration.",
            "Attendance is mandatory. Email before lab if you will miss it, or that lab is a zero.",
            "No lab is dropped. Labs are 5% of the grade.",
            "Bring a laptop and a printed lab report. Excel is required. One hard-copy report per pair.",
            "The lab syllabus says finish during the 50 minutes or turn the report in by midnight that Monday. The lecture syllabus says within 7 days. Use midnight unless the TA says otherwise.",
            conflict,
            "",
            LAB_SCHEDULE,
        ]),
        "ECJ 2.218",
        start_t,
        end_t,
    )
for day, activity, detail, kind in CE311S_LABS:
    allday(
        "CE 311S",
        day,
        activity,
        detail,
        block_note([
            f"Monday lab in ECJ 2.218. This date is {activity}: {detail}.",
            "Keep only your unique-number lab series (17645 at 1–2, 17655 at 2–3, 17660 at 3–4, or 17650 at 4–5).",
            "Numbered labs: turn the report in by midnight tonight if you do not finish in the room.",
            "Review days: no numbered lab report. The review prepares you for the in-class exam.",
        ]),
        alarms=["PT8H"] if kind == "review" else DUE_ALLDAY_ALARMS,
    )

series(
    "CE 311S", date(2026, 8, 26), date(2026, 12, 4), {2, 4},
    "Office hours", "Dr. Kockelman",
    "Wednesday and Friday, 12:30–2:00 pm, ECJ 6.904. You can also call 512-471-0210 or email kkockelm@mail.utexas.edu.",
    "ECJ 6.904", time(12, 30), time(14, 0), busy=False, alarms=[],
)
series(
    "CE 311S", date(2026, 8, 25), date(2026, 12, 3), {1, 3},
    "Office hours", "TA Khan",
    "Sadab Khan, lead TA. Tuesday and Thursday, 3:00–5:00 pm, 6th floor TA room in ECJ (just past the bathrooms). sk67837@my.utexas.edu. Also runs Monday labs and exam reviews.",
    "ECJ 6th floor TA room", time(15, 0), time(17, 0), busy=False, alarms=[],
)
series(
    "CE 311S", date(2026, 8, 26), date(2026, 12, 2), {2},
    "Office hours", "Tutor Grotewold",
    "Zachary Grotewold, undergraduate tutor, about 5 hours a week. Wednesday 3:00–4:00 pm, ECJ 3.108. zkg228@my.utexas.edu. These hours are a starting schedule.",
    "ECJ 3.108", time(15, 0), time(16, 0), busy=False, alarms=[],
)
series(
    "CE 311S", date(2026, 8, 28), date(2026, 12, 4), {4},
    "Office hours", "Tutor Grotewold",
    "Zachary Grotewold. Friday 12:00–3:00 pm, ECJ 3.108. zkg228@my.utexas.edu. Overlaps Dr. Kockelman's Friday office hours from 12:30–2:00, which is fine: both are drop-in help.",
    "ECJ 3.108", time(12, 0), time(15, 0), busy=False, alarms=[],
)

allday(
    "CE 311S",
    date(2026, 9, 21),
    "Deadline",
    "Check the final exam time",
    "The lab syllabus says final-exam schedules are posted on September 21. CE 311S final is still TBA in the syllabus. ME 310T also says its final time is finalized by this date. Open the registrar schedule and update those events.",
    importance="2",
)
allday(
    "CE 311S",
    date(2026, 12, 8),
    "Deadline",
    "Final exam is still TBA",
    "Study days are December 8–9. The CE 311S final was not given a date or room in the syllabus. Do not leave Austin until you have checked the registrar time. The lecture syllabus says it may be a standard 3-hour final and that students might pick among times UT offers.",
    importance="2",
)

# ---------------------------------------------------------------------------
# EM 306
# ---------------------------------------------------------------------------

EM_WEEKS = [
    (date(2026, 8, 24), date(2026, 8, 28), "Introduction, mechanics, and force"),
    (date(2026, 8, 31), date(2026, 9, 4), "Force and moment"),
    (date(2026, 9, 9), date(2026, 9, 11), "Couples and free-body diagrams"),
    (date(2026, 9, 14), date(2026, 9, 18), "Equilibrium and 2D problems"),
    (date(2026, 9, 21), date(2026, 9, 25), "Plane trusses: joints and sections"),
    (date(2026, 9, 28), date(2026, 10, 2), "Frames and review"),
    (date(2026, 10, 5), date(2026, 10, 9), "Distributed loads"),
    (date(2026, 10, 12), date(2026, 10, 16), "Beams, internal forces, and moments"),
    (date(2026, 10, 19), date(2026, 10, 23), "Shear and bending-moment diagrams"),
    (date(2026, 10, 26), date(2026, 10, 30), "Vector algebra and review"),
    (date(2026, 11, 2), date(2026, 11, 6), "3D force systems and equilibrium"),
    (date(2026, 11, 9), date(2026, 11, 13), "3D equilibrium"),
    (date(2026, 11, 16), date(2026, 11, 20), "Dry friction"),
    (date(2026, 11, 30), date(2026, 12, 4), "Centroids and area moments of inertia"),
]

def em_topic(day: date) -> str:
    for start, end, topic in EM_WEEKS:
        if start <= day <= end:
            return topic
    return "Review"


for day in days(FIRST, LAST_CLASS, {0, 2, 4}):
    topic = "Review" if day == date(2026, 12, 7) else em_topic(day)
    hw = ""
    if day.weekday() == 2 and day != date(2026, 12, 2):
        hw = " Homework is typically assigned on Wednesday and due the following Friday. Canvas has the actual problem set. Late homework is not accepted unless Dr. Kalina approves it in person. This calendar does not invent those Friday dates."
    if day == date(2026, 12, 2):
        hw = " This is the last Wednesday. Do not assume a new homework is assigned today unless Canvas says so."
    meeting(
        "EM 306",
        day,
        "Lecture",
        topic,
        block_note([
            "EM 306 Statics. Mon/Wed/Fri 1:00–2:00 pm, PAI 3.02.",
            "Dr. Ryan Kalina, r.kalina@utexas.edu. Primary office ASE 5.238. Secondary office ECJ 4.734.",
            "The syllabus gives the topic by week, not by day, so each meeting this week carries the same topic.",
            "An attendance quiz is given every lecture. Five misses are allowed before the attendance grade drops.",
            hw,
            "If class is cancelled for a conference, a make-up recording is posted on Canvas.",
        ]),
        "PAI 3.02",
        time(13, 0),
        time(14, 0),
    )

EM_EXAMS = [
    (date(2026, 9, 29), "Exam 1"),
    (date(2026, 10, 27), "Exam 2"),
    (date(2026, 12, 1), "Exam 3"),
]
for day, name in EM_EXAMS:
    for label, start_t, end_t, sections in (
        ("4–6pm seating", time(16, 0), time(18, 0), "#16220 and #16225 meet at 4:00, so this is the likely seating if your discussion starts at 4:00. Confirm on Canvas."),
        ("6–8pm seating", time(18, 0), time(20, 0), "#16230 and #16235 meet at 6:00, so this is the likely seating if your discussion starts at 6:00. Confirm on Canvas."),
    ):
        meeting(
            "EM 306",
            day,
            "Exam",
            f"{name} · {label}",
            block_note([
                f"{name} is a two-hour evening exam. Both seatings are on the syllabus: 4:00–6:00 pm and 6:00–8:00 pm.",
                "DELETE the seating that is not yours after the room list is posted.",
                sections,
                "Closed book and notes. Calculators are allowed. No phones, watches, or earbuds. Bring your student ID.",
                "No make-up exams. Rooms are posted on Canvas before the exam.",
                "Weight depends on whether this is your lowest, middle, or highest midterm: 15%, 17.5%, or 22.5%.",
                "There is no discussion quiz on this evening. The discussion is the exam.",
            ]),
            "Room posted on Canvas",
            start_t,
            end_t,
            alarms=EXAM_ALARMS,
            importance="2",
        )

meeting(
    "EM 306",
    date(2026, 12, 11),
    "Exam",
    "Final · 1–3pm",
    block_note([
        "Friday, December 11, 1:00–3:00 pm.",
        "Do not schedule travel over this time. No early exams.",
        "The room is not named. The regular classroom is PAI 3.02; confirm the final room on the registrar schedule.",
        "Worth 25%. Closed book and notes.",
    ]),
    "See registrar schedule",
    time(13, 0),
    time(15, 0),
    alarms=EXAM_ALARMS,
    importance="2",
)

EM_DISCUSSIONS = [
    ("16220", "Juliette Noyer", {0}, time(16, 0), time(18, 0), "CPE 2.220", date(2026, 8, 24), LAST_CLASS,
     "Overlaps CE 311S lab #17650 (Mon 4:00–5:00 pm)."),
    ("16225", "Junyoung Kim", {1}, time(16, 0), time(18, 0), "ECJ 1.314", date(2026, 8, 25), date(2026, 12, 1),
     "Same time as CE 311K lab #17620 (Tue 4:00–6:00 pm)."),
    ("16230", "Rowan Williams", {0}, time(18, 0), time(20, 0), "ECJ 1.314", date(2026, 8, 24), LAST_CLASS, ""),
    ("16235", "Junyoung Kim", {1}, time(18, 0), time(20, 0), "ECJ 1.314", date(2026, 8, 25), date(2026, 12, 1), ""),
]
EXAM_NIGHTS = {date(2026, 9, 29), date(2026, 10, 27), date(2026, 12, 1)}
for unique, ta, weekdays, start_t, end_t, room, start_d, end_d, conflict in EM_DISCUSSIONS:
    series(
        "EM 306",
        start_d,
        end_d,
        weekdays,
        "Discussion + Quiz",
        f"#{unique}",
        block_note([
            f"DELETE this whole series if your unique number is not {unique}.",
            "In Outlook, open any one of these and choose Delete series.",
            f"TA {ta}. {room}.",
            "A quiz is given every discussion unless the instructor announces otherwise. No make-up quizzes.",
            "Be in the room within 2 minutes of the start. Later arrival lowers the quiz score.",
            "You must take the quiz in the section you are registered for.",
            "Discussions are the best place to ask about homework.",
            "Tuesday exam evenings (Sep 29, Oct 27, Dec 1) are not discussions. Those nights are the exams.",
            conflict,
        ]),
        room,
        start_t,
        end_t,
        extra_skip=EXAM_NIGHTS,
    )

series(
    "EM 306",
    date(2026, 8, 26),
    date(2026, 12, 2),
    {2},
    "Office hours",
    "Dr. Kalina",
    block_note([
        "Wednesday 4:00–5:00 pm on days when class is held, or by appointment.",
        "Primary office ASE 5.238. Secondary office ECJ 4.734. The door-open policy also applies when he is in either office.",
        "r.kalina@utexas.edu.",
    ]),
    "ASE 5.238",
    time(16, 0),
    time(17, 0),
    busy=False,
    alarms=[],
)

# ---------------------------------------------------------------------------
# ARE 217 — no assignment calendar in the syllabus
# ---------------------------------------------------------------------------

ARE217 = [
    ("17445", "MW 8–10am", time(8, 0), time(10, 0), "Stephen Smith", "stephen.smith@utexas.edu", ""),
    ("17450", "MW 10am–12pm", time(10, 0), time(12, 0), "Reese Smiley", "reese.smiley@utexas.edu",
     "Overlaps CE 311S lecture at 11:00–11:50 am. The syllabus writes the end time as 12:00 a.m.; that is treated here as noon."),
    ("17455", "MW 3–5pm", time(15, 0), time(17, 0), "Sofia Leal Cavazos", "sofia.leal@utexas.edu",
     "On Wednesday this starts at 3:00 pm, when ARE 102 ends."),
    ("17460", "MW 5–7pm", time(17, 0), time(19, 0), "Sofia Leal Cavazos", "sofia.leal@utexas.edu", ""),
]
for unique, label, start_t, end_t, ta, email, note in ARE217:
    series(
        "ARE 217",
        FIRST,
        LAST_CLASS,
        {0, 2},
        "Studio",
        f"#{unique} · {label}",
        block_note([
            f"DELETE this whole series if your unique number is not {unique}.",
            "In Outlook, open any one of these and choose Delete series.",
            "If you are not taking ARE 217 in Fall 2026, delete all four series.",
            "The PDF header says Fall 2027. The file name says Fall 2026, and the PDF was created August 23, 2026. These meetings are placed on the Fall 2026 Monday/Wednesday calendar.",
            f"Thomas Taylor Design Studio, ECJ 3.106. TA {ta}, {email}.",
            "Instructor: Peter Johnson, peter.johnson@austin.utexas.edu, ECJ 4.406. Office hours are by appointment only.",
            "Tutor hours in ECJ 3.106 will be posted on Canvas. They are not in the syllabus, so they are not on this calendar.",
            "The syllabus has no dated homework, quizzes, or exams.",
            "Attendance is 10% of the grade. Three unexcused absences lower the course grade by a full letter.",
            note,
        ]),
        "ECJ 3.106",
        start_t,
        end_t,
    )

allday(
    "ARE 217",
    FIRST,
    "Note",
    "No dated assignments in the syllabus",
    "ARE 217's syllabus has studio times and no schedule of due dates. Tutor hours are 'to be posted to Canvas.' Professor office hours are by appointment. Check Canvas each week and add those dates when they appear.",
    alarms=["PT9H"],
)

# ---------------------------------------------------------------------------
# University dates that the syllabi rely on
# ---------------------------------------------------------------------------

allday(
    "UT Austin",
    date(2026, 9, 7),
    "No class",
    "Labor Day",
    "No classes. Monday labs, discussions, lectures, and office hours are already left off this calendar.",
    alarms=[],
)
allday(
    "UT Austin",
    date(2026, 9, 9),
    "Deadline",
    "Last drop without permission",
    "12th class day. EM 306 lists this as the last day to drop a course without permission. It is also the university date.",
    importance="2",
)
allday(
    "UT Austin",
    date(2026, 11, 18),
    "Deadline",
    "Last Q-drop",
    "EM 306 lists November 18 as the last day to Q-drop, withdraw, or change to or from pass/fail. This matches the university undergraduate deadline.",
    importance="2",
)
allday(
    "UT Austin",
    date(2026, 11, 23),
    "No class",
    "Fall break through Nov 28",
    "No classes November 23–28. Those lectures, labs, discussions, and office hours are already left off this calendar. Classes resume Monday, November 30.",
    alarms=[],
)
allday(
    "UT Austin",
    date(2026, 12, 7),
    "Last class day",
    "",
    "Last class day for Fall 2026. December 8–9 are study days. Final exams are December 10, 11, 12, and 14.",
    alarms=["PT9H"],
)
allday(
    "UT Austin",
    date(2026, 12, 8),
    "Study day",
    "Also Dec 9",
    "No classes. Use this for CE 311S final-exam review if you still do not have a time, and for ME 310T and EM 306 finals later in the week.",
    alarms=[],
)

# Setup event the day before classes.
allday(
    "UT Austin",
    date(2026, 8, 23),
    "Start here",
    "Color the classes, delete extra sections",
    block_note([
        "This calendar was built from your Fall 2026 syllabi.",
        "",
        "Color in Outlook, one time: open any event, choose Categorize, and set",
        "ARE 102 = blue, ARE 217 = purple, CE 311K = orange, CE 311S = green, EM 306 = red, ME 310T = yellow, UT Austin = dark gray.",
        "The colored square in the title already shows the class before you do that.",
        "The word after the square is the activity: Lecture, Exam, Quiz, HW due, Lab, Studio, Office hours, Reading due, Project due.",
        "Search the calendar for Exam or HW due when you only want those.",
        "",
        "Delete the sections that are not yours. Open one event and delete the series:",
        "CE 311K labs: 17605 Fri 12–2, 17610 Fri 2–4, 17615 Wed 3–5, 17620 Tue 4–6. All in ECJ 2.210.",
        "CE 311S Monday labs in ECJ 2.218: 17645 1–2, 17655 2–3, 17660 3–4, 17650 4–5. Confirm the unique number on your registration; the two syllabi list them in different orders. A separate all-day event each Monday names that week's lab or review. Keep that one.",
        "EM 306 discussions: 16220 Mon 4–6 CPE 2.220, 16225 Tue 4–6 ECJ 1.314, 16230 Mon 6–8 ECJ 1.314, 16235 Tue 6–8 ECJ 1.314.",
        "EM 306 evening exams are listed twice (4–6 and 6–8). Delete the seating that is not yours after Canvas posts rooms.",
        "ARE 217 studios in ECJ 3.106: 17445 MW 8–10, 17450 MW 10–12, 17455 MW 3–5, 17460 MW 5–7. The PDF header says Fall 2027. Delete all four if you are not in it this fall.",
        "",
        "Office hours and optional recitations are marked free, so they show up but do not block your day, and they do not alarm.",
        "",
        "ES 333T was pasted without a course schedule, meeting time, or due dates. Nothing from that course is on this calendar. Send the schedule page if you want it added.",
        "",
        "Not dated in the syllabi, so not invented here: CE 311K homework, CE 311S homework, EM 306 homework (typically assigned Wednesday and due the next Friday), ARE 217 assignments, and the CE 311S final exam time.",
        "",
        "Confirm these conflicts in the syllabi before you trust them:",
        "ARE 102 Project 1 is October 2 in one place and October 28 in another.",
        "CE 311K Midterm 2 names Thursday, November 19, but not the clock time. It is placed in the regular 8:00 am class.",
        "ME 310T homework is placed at Friday 9:00 pm, which is the written rule. The schedule table shows each homework on the Thursday row.",
    ]),
    alarms=["PT9H"],
    importance="2",
)


def ics_escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\n", "\\n")
        .replace(",", "\\,")
        .replace(";", "\\;")
    )


def fold(line: str) -> str:
    raw = line.encode("utf-8")
    chunks = []
    while len(raw) > 73:
        cut = 73
        while cut > 0 and (raw[cut] & 0xC0) == 0x80:
            cut -= 1
        chunks.append(raw[:cut].decode("utf-8"))
        raw = raw[cut:]
    chunks.append(raw.decode("utf-8"))
    return "\r\n ".join(chunks)


def fmt_local(day: date, clock: time) -> str:
    return datetime.combine(day, clock, TZ).strftime("%Y%m%dT%H%M%S")


def render() -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//UT Fall 2026//Syllabus Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:UT Fall 2026 Classes",
        "X-WR-TIMEZONE:America/Chicago",
        "X-WR-CALDESC:Fall 2026 classes\\, exams\\, homework\\, and office hours from your syllabi.",
        "BEGIN:VTIMEZONE",
        "TZID:America/Chicago",
        "X-LIC-LOCATION:America/Chicago",
        "BEGIN:DAYLIGHT",
        "TZOFFSETFROM:-0600",
        "TZOFFSETTO:-0500",
        "TZNAME:CDT",
        "DTSTART:19700308T020000",
        "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU",
        "END:DAYLIGHT",
        "BEGIN:STANDARD",
        "TZOFFSETFROM:-0500",
        "TZOFFSETTO:-0600",
        "TZNAME:CST",
        "DTSTART:19701101T020000",
        "RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU",
        "END:STANDARD",
        "END:VTIMEZONE",
    ]
    seen = set()
    for i, ev in enumerate(sorted(EVENTS, key=lambda e: (e["day"], e["start"] or time(0, 0), e["summary"]))):
        uid = f"{ev['day'].strftime('%Y%m%d')}-{i}-{ev['category'].replace(' ', '')}@ut-fall-2026"
        if uid in seen:
            raise RuntimeError(uid)
        seen.add(uid)
        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{uid}")
        lines.append(f"DTSTAMP:{stamp}")
        if ev["start"] is None:
            lines.append(f"DTSTART;VALUE=DATE:{ev['day'].strftime('%Y%m%d')}")
            lines.append(f"DTEND;VALUE=DATE:{(ev['day'] + timedelta(days=1)).strftime('%Y%m%d')}")
            lines.append("X-MICROSOFT-CDO-ALLDAYEVENT:TRUE")
        else:
            lines.append(f"DTSTART;TZID=America/Chicago:{fmt_local(ev['day'], ev['start'])}")
            lines.append(f"DTEND;TZID=America/Chicago:{fmt_local(ev['day'], ev['end'])}")
            lines.append("X-MICROSOFT-CDO-ALLDAYEVENT:FALSE")
            if ev["rrule"]:
                lines.append(f"RRULE:{ev['rrule']}")
                for skipped in ev["exdates"]:
                    lines.append(
                        f"EXDATE;TZID=America/Chicago:{fmt_local(skipped, ev['start'])}"
                    )
        lines.append(f"SUMMARY:{ics_escape(ev['summary'])}")
        if ev["location"]:
            lines.append(f"LOCATION:{ics_escape(ev['location'])}")
        lines.append(f"DESCRIPTION:{ics_escape(ev['description'])}")
        lines.append(f"CATEGORIES:{ics_escape(ev['category'])}")
        lines.append("STATUS:CONFIRMED")
        lines.append("TRANSP:" + ("OPAQUE" if ev["busy"] else "TRANSPARENT"))
        lines.append("X-MICROSOFT-CDO-BUSYSTATUS:" + ("BUSY" if ev["busy"] else "FREE"))
        lines.append(f"X-MICROSOFT-CDO-IMPORTANCE:{ev['importance']}")
        lines.append("PRIORITY:" + ("1" if ev["importance"] == "2" else "5"))
        for trigger in ev["alarms"]:
            lines.append("BEGIN:VALARM")
            lines.append("ACTION:DISPLAY")
            lines.append(f"DESCRIPTION:{ics_escape(ev['summary'])}")
            lines.append(f"TRIGGER:{trigger}")
            lines.append("END:VALARM")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(line) for line in lines) + "\r\n"


def main():
    assert date(2026, 8, 24).weekday() == 0
    assert date(2026, 12, 7).weekday() == 0
    assert date(2026, 11, 26).weekday() == 3
    text = render()
    path = "Fall-2026-Outlook-Calendar.ics"
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

    from collections import Counter
    counts = Counter((e["category"], e["activity"]) for e in EVENTS)
    print(f"events {len(EVENTS)}")
    for key in sorted(counts):
        print(f"  {key[0]:10} {key[1]:22} {counts[key]}")

    holiday_hits = [
        e for e in EVENTS
        if e["day"] in SKIP and "No class" not in e["summary"] and "Fall break" not in e["summary"]
    ]
    print("holiday hits", len(holiday_hits))
    for e in holiday_hits:
        print(" ", e["day"], e["summary"])

    print("\nEXAMS AND DUE DATES")
    for e in sorted(EVENTS, key=lambda x: (x["day"], x["start"] or time(0, 0), x["summary"])):
        if e["activity"] in {"Exam", "HW due", "Optional HW fix", "Project 1 due", "Project 2 due", "Notebook due", "Notebook cutoff", "Reading due", "Deadline", "Checkpoint"} or e["activity"].startswith("Project"):
            clock = e["start"].strftime("%H:%M") if e["start"] else "all day"
            print(f"{e['day']} {clock}  {e['summary']}")


if __name__ == "__main__":
    main()
