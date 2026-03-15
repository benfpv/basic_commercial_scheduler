# basic_commercial_scheduler

A Python scheduling system for managing multi-party availability, commitments, and meetings — backed by SQLite3 and built with `datetime` / `zoneinfo` for full timezone support.

---

## Scheduling Pipeline

Scheduling progresses through four ordered stages:

```
Availability → Intersections → Commitments → Meetings
```

| Stage | Description |
|---|---|
| **Availability** | Time windows when a person is free |
| **Intersections** | Overlapping availability across all selected persons |
| **Commitments** | Confirmed slots — all selected persons are booked |
| **Meetings** | Commitments that have been realized (attended, logged, billed) |

Each transition is explicit and auditable. Commitment rows are preserved in the DB even after promotion to meetings (audit trail).

---

## Project Structure

```
basic_commercial_scheduler/
├── run_admin.py          # Entry point: terminal admin UI
├── run_demo.py           # Entry point: exercises all Persons/Person endpoints
├── check_db.py           # Utility: inspect DB tables
│
├── classes/
│   ├── persons.py        # Persons — container/orchestrator for all Person objects
│   └── person.py         # Person — individual profile + scheduling data
│
├── db/
│   └── database.py       # SQLite3 layer (init, execute, insert, fetch)
│
├── ui/
│   ├── functions_calendar_ui_admin.py      # Time slot picker
│   ├── functions_plan_meeting_ui_admin.py  # Intersection → commitment confirmation
│   └── functions_user_register_ui_admin.py # Person registration form
│
└── data_pilot/
    └── scheduler.db      # SQLite database (auto-created on first run)
```

---

## Database Schema

| Table | Purpose |
|---|---|
| `users` | Person master record (role, name, rate, balance, timezone, …) |
| `user_availabilities` | Per-person available time windows |
| `commitments` | Group-level committed slot |
| `commitment_participants` | Which users belong to each commitment |
| `meetings` | Realized meetings; FK back to originating commitment |
| `meeting_participants` | Who was scheduled + attended flag |
| `balance_history` | Per-person financial trail, linked to a meeting |

All datetimes are stored as UTC strings (`"%Y-%m-%d %H:%M:%S%z"`). Scheduling lists use the format `[ids_str, start_utc, end_utc]` where multi-person IDs are joined as `"id1&id2&id3"`.

---

## Key Classes

### `Persons` (`classes/persons.py`)
Orchestrates the full scheduling lifecycle across all persons.

```python
persons = Persons("America/Toronto")
persons.update()                                    # refresh datetimes, promote commitments → meetings
persons.search_generically("mario")                 # fuzzy-match across all fields
persons.search_by_key("role", "teacher")            # search by specific attribute
persons.append_selected_person(person)              # add to working selection
persons.get_intersecting_availability()             # compute overlapping availability
persons.create_intersecting_commitments()           # commit selected intersections
persons.update_commitments_to_meetings()            # promote past commitments to meetings
```

### `Person` (`classes/person.py`)
Holds a single person's profile and scheduling data. All persistence is DB-only.

```python
person.availability      # list of [id, start_utc, end_utc]
person.commitments       # list of [id, start_utc, end_utc]
person.meetings_history  # list of [id, start_utc, end_utc]
person.balance_history   # list of [user_id, associate_ids, start_utc, end_utc, amount, balance_after]
```

---

## Getting Started

**Requirements:** Python 3.9+, no external dependencies.

```bash
# Admin terminal UI
python run_admin.py

# Run all endpoint demos (non-interactive)
python run_demo.py

# Inspect the database
python check_db.py
```

The SQLite database is created automatically at `data_pilot/scheduler.db` on first run.

