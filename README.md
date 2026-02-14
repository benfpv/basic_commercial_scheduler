# basic_commercial_scheduler
*WIP*  
Basic commercial-scale scheduler (+ demo terminal-based frontend) to bulk-manage availabilities, availability intersections, commitments, and meetings among any number of persons; by leveraging Python's built-in `datetime` and `zoneinfo` modules.

---

## Overview

`basic_commercial_scheduler` is designed for structured, multi-party scheduling workflows where coordination, confirmation, and post-meeting processing all matter.

The system models scheduling in four progressive stages:
- 1. Availability
Time slots where a person is available.
- 2. Intersections
Time slots where *all persons in a selected group* are available.
- 3. Commitments
Time slots where *all persons in a selected group* have committed to meeting.
- 4. Meetings
Commitments that have actually resulted in a meeting (based on supporting evidence).
- 5. Post-Processing
WIP

---

## Example Workflow (Demo Frontend)

### (1) Main Menu
```text
============================== Init UI ==============================

=================== MAIN MENU ===================

[0]: print_selected
[1]: print_global_commitments
[2]: register_person
[3]: search
[4]: search_by_key
[5]: print_availability
[6]: create_availability
[7]: remove_availability
[8]: find_intersection
[9]: clear_working_memory
[10]: exit

---------- Please Enter Index: ----------
```
---

### (2) Search for & Select Persons
Search by name or category and build a working group.
```text
============================== SEARCH ==============================

---------- Search Generically For Values (Separated by Space) (Enter '' to go back): ----------
mario

------ search_generically() for 'mario' ------

Matched Persons [2]:
- Person: student, Mario, Mario, 38, 18, 2026-02-25, 2010-09-13, 1 Mushroom Kingdom Road, +1 555-000-1111, mario@nintendo.fake, 70, 100, America/New_York, plumber in training
- Person: student, Luigi, Mario, 39, 18, 2026-02-25, 2011-06-01, 1 Mushroom Kingdom Road, +1 555-000-2222, luigi@nintendo.fake, 65, 0, America/New_York,

---------- Matches [n=2]: ----------

[0]: Person: student, Mario, Mario, 38, 18, 2026-02-25, 2010-09-13, 1 Mushroom Kingdom Road, +1 555-000-1111, mario@nintendo.fake, 70, 100, America/New_York, plumber in training
[1]: Person: student, Luigi, Mario, 39, 18, 2026-02-25, 2011-06-01, 1 Mushroom Kingdom Road, +1 555-000-2222, luigi@nintendo.fake, 65, 0, America/New_York,

---------- Please Enter Indices (Separated by Space) to Add to Selection (Enter '' to go back): ----------



============================== SEARCH ==============================

---------- Search Generically For Values (Separated by Space) (Enter '' to go back): ----------
teacher

------ search_generically() for 'teacher' ------

Matched Persons [8]:
- Person: teacher, Kratos, Spartan, 48, 14, 2026-03-02, 1985-01-01, 400 Mount Olympus, +1 555-555-1111, kratos@godofwar.fake, 120, 0, America/New_York, anger management pending
- Person: teacher, Atreus, Loki, 49, 14, 2026-03-02, 2008-11-30, 400 Mount Olympus, +1 555-555-2222, atreus@godofwar.fake, 85, 60, America/New_York,
- Person: teacher, Master, Chief, 50, 15, 2026-03-03, 1987-03-07, 117 Halo Ring, +1 555-666-1177, chief@halo.fake, 110, 0, America/Chicago, tactical training
- Person: teacher, Cortana, AI, 51, 15, 2026-03-03, 1999-11-07, 117 Halo Ring, +1 555-666-0001, cortana@halo.fake, 100, -50, America/Chicago, system glitch
- Person: teacher, Geralt, Rivia, 52, 16, 2026-03-04, 1983-05-05, 13 Kaer Morhen Keep, +1 555-777-1313, geralt@witcher.fake, 95, 200, America/Denver, monster hunting fee
- Person: teacher, Yennefer, Vengerberg, 53, 16, 2026-03-04, 1988-09-19, 13 Kaer Morhen Keep, +1 555-777-1919, yennefer@witcher.fake, 105, 0, America/Denver,
- Person: teacher, Lara, Croft, 56, 17, 2026-03-06, 1992-02-14, 1 Croft Manor, +1 555-999-0001, lara@tombraider.fake, 100, 500, America/New_York, archaeology specialist
- Person: teacher, Nathan, Drake, 57, 17, 2026-03-06, 1989-01-01, 22 Uncharted Island, +1 555-999-2222, nathan@uncharted.fake, 95, 75, America/New_York, treasure hunting leave

---------- Matches [n=8]: ----------

[0]: Person: teacher, Kratos, Spartan, 48, 14, 2026-03-02, 1985-01-01, 400 Mount Olympus, +1 555-555-1111, kratos@godofwar.fake, 120, 0, America/New_York, anger management pending
[1]: Person: teacher, Atreus, Loki, 49, 14, 2026-03-02, 2008-11-30, 400 Mount Olympus, +1 555-555-2222, atreus@godofwar.fake, 85, 60, America/New_York,
[2]: Person: teacher, Master, Chief, 50, 15, 2026-03-03, 1987-03-07, 117 Halo Ring, +1 555-666-1177, chief@halo.fake, 110, 0, America/Chicago, tactical training
[3]: Person: teacher, Cortana, AI, 51, 15, 2026-03-03, 1999-11-07, 117 Halo Ring, +1 555-666-0001, cortana@halo.fake, 100, -50, America/Chicago, system glitch
[4]: Person: teacher, Geralt, Rivia, 52, 16, 2026-03-04, 1983-05-05, 13 Kaer Morhen Keep, +1 555-777-1313, geralt@witcher.fake, 95, 200, America/Denver, monster hunting fee
[5]: Person: teacher, Yennefer, Vengerberg, 53, 16, 2026-03-04, 1988-09-19, 13 Kaer Morhen Keep, +1 555-777-1919, yennefer@witcher.fake, 105, 0, America/Denver,
[6]: Person: teacher, Lara, Croft, 56, 17, 2026-03-06, 1992-02-14, 1 Croft Manor, +1 555-999-0001, lara@tombraider.fake, 100, 500, America/New_York, archaeology specialist
[7]: Person: teacher, Nathan, Drake, 57, 17, 2026-03-06, 1989-01-01, 22 Uncharted Island, +1 555-999-2222, nathan@uncharted.fake, 95, 75, America/New_York, treasure hunting leave

---------- Please Enter Indices (Separated by Space) to Add to Selection (Enter '' to go back): ----------
3

------ append_selected() ------

...Press Enter to Continue...
```
---

### (3) Manage Availabilities
Create, edit, or remove availability windows for selected persons.
```text
==================== CREATE AVAILABILITY [For Selected] ====================

Select multiple time slots. Type 'done' when finished.

Add a new slot? (y/done): y

        February 2026
Mo Tu We Th Fr Sa Su
                   1
 2  3  4  5  6  7  8
 9 10 11 12 13 14 15
16 17 18 19 20 21 22
23 24 25 26 27 28

Enter day number (or 'q' to cancel): 14
Enter start time (HH:MM, 24h): 13
Invalid time format.
Enter start time (HH:MM, 24h): 13:00
Enter duration (minutes): 16:00
Invalid duration.
Enter duration (minutes): 60
Slot added: 2026-02-14 13:00:00+00:00 to 2026-02-14 14:00:00+00:00 (UTC)

Add a new slot? (y/done): done

You selected the following slots:
1. 2026-02-14 13:00:00+00:00 to 2026-02-14 14:00:00+00:00 (UTC)
Confirm? (y/n): y
```
---

### (4) Infer Availability Intersections
Automatically compute overlapping time slots across the selected group.  
These intersections become candidate commitments.
```text
==================== FIND INTERSECTION [For Selected] ====================

----- get_intersecting_availability() -----

Availability 1/3 [1]:
[['38', '2026-02-14 12:00:00+00:00', '2026-02-15 00:00:00+00:00']]

Availability 2/3 [1]:
[['39', '2026-02-14 12:00:00+00:00', '2026-02-15 00:00:00+00:00']]

Availability 3/3 [2]:
[['51', '2026-02-14 12:00:00+00:00', '2026-02-14 13:00:00+00:00'],
 ['51', '2026-02-14 14:00:00+00:00', '2026-02-15 00:00:00+00:00']]

Availability Intersections [2]:
[['38&39&51', '2026-02-14 12:00:00+00:00', '2026-02-14 13:00:00+00:00'],
 ['38&39&51', '2026-02-14 14:00:00+00:00', '2026-02-15 00:00:00+00:00']]

----- Intersections -----

[0]: ['38&39&51', '2026-02-14 12:00:00+00:00', '2026-02-14 13:00:00+00:00']
[1]: ['38&39&51', '2026-02-14 14:00:00+00:00', '2026-02-15 00:00:00+00:00']

--------- Please Enter Indices of Intersections to Commit (Enter '' to go back): ---------
```
---

### (5) Create & Access Commitments
Convert intersection windows into formal commitments.
```text
==================== PRINT GLOBAL COMMITMENTS ====================

----- print_global_commitments() -----

Global Commitments [1]:
- ['51&38&39', '2026-02-14 12:00:00+00:00', '2026-02-14 13:00:00+00:00']

Press Enter to Continue...
```
---

### (6) Formalize Commitments into Meetings *(WIP)*

Commitments may be finalized into:

- Full meetings  
- Partial meetings  
- Non-meetings  

Formalization may depend on:

- Attendance evidence  
- Duration confirmation  
- Manual verification  

---

### (7) Process Scheduling Outcomes *(WIP)*

Once meetings are finalized, downstream processing may include:

- Payout calculation (based on rate & duration)  
- Reporting  
- Aggregation across participants  

---

## Design Goals

- Scalable group coordination  
- Time zone correctness (via `zoneinfo`)  
- Deterministic intersection logic  
- Commercial workflow alignment  
- Clear separation of scheduling states  
- Backend-first architecture with pluggable frontends  

---

## Tech Stack

- Python 3.9+  
- `datetime`  
- `zoneinfo`  
- Terminal-based interface (demo layer)

---
