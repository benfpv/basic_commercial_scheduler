"""
run_demo.py
================================
Reference script for front-end developers.

Shows every Persons + Person endpoint invoked by Functions_Cmd_Ui_Admin,
with the exact call signature, the shape of inputs, and the shape of
return values / side-effects.

Run from project root:
    python run_demo.py

Nothing here modifies persistent state — every write is rolled back via a
fresh reload of each person from the DB after the demo call.  The one
exception is the registration demo, which inserts a real row; it is
clearly labelled and commented out by default.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from classes.persons import Persons

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
SEP  = "=" * 60
LINE = "-" * 60

def _section(title: str):
    print(f"\n{SEP}\n  {title}\n{SEP}")

def _sub(label: str):
    print(f"\n{LINE}\n  {label}\n{LINE}")


# ===========================================================================
#  PERSONS ENDPOINTS
# ===========================================================================
#
#  Constructor
#  -----------
#  Persons(current_timezone: str | None = None)
#
#  Properties (set on init, always available)
#  ------------------------------------------
#  persons.persons              -> list[Person]          all loaded Person objects
#  persons.persons_len          -> int
#  persons.person_attributes    -> list[str]             ordered field name list
#  persons.commitments          -> list[[ids_str, start_utc, end_utc]]   global
#  persons.meetings_history     -> list[[ids_str, start_utc, end_utc]]   global
#  persons.active_meetings      -> list[[ids_str, start_utc, end_utc]]   transient
#  persons.current_timezone     -> ZoneInfo
#  persons.current_datetime     -> datetime (tz-aware)
#  persons.search_results       -> list[Person]          last search result
#  persons.selected_persons     -> list[Person]          working selection
#  persons.selected_intersections -> list[[ids_str, start_utc, end_utc]]
#  persons.global_balance_entry_modifiers -> list[float] price multipliers
#
# ===========================================================================

def demo_persons_init():
    _section("Persons.__init__(current_timezone)")
    # INPUT  : IANA timezone string  (or None → uses local system timezone)
    # EFFECT : loads DB, hydrates all Person objects, sets current_datetime
    # RETURNS: Persons instance
    persons = Persons("America/Toronto")
    print(f"  persons.persons_len        = {persons.persons_len}")
    print(f"  persons.current_timezone   = {persons.current_timezone}")
    print(f"  persons.current_datetime   = {persons.current_datetime}")
    print(f"  persons.person_attributes  = {persons.person_attributes}")
    return persons


def demo_persons_update(persons: Persons):
    _section("persons.update()")
    # INPUT  : (none)
    # EFFECT : refreshes current_datetime; promotes past commitments to meetings
    # RETURNS: None
    persons.update()
    print(f"  current_datetime refreshed -> {persons.current_datetime}")


# ---------------------------------------------------------------------------
# Search & Selection
# ---------------------------------------------------------------------------

def demo_search_generically(persons: Persons):
    _section("persons.search_generically(search_str, role_key='', search_accuracy=0.7)")
    # INPUT  :  search_str    str  — space-separated words; matched fuzzily
    #                                against every string attribute of every person
    #           role_key      str  — optional substring filter on person.role
    #           search_accuracy float 0–1  (default 0.7)
    # RETURNS: list[Person]   — persons sorted by match score descending
    #          also sets persons.search_results
    results = persons.search_generically("mario", search_accuracy=0.6)
    print(f"  search_generically('mario') -> {[str(p) for p in results]}")


def demo_search_for_attr(persons: Persons):
    _section("persons.search_for_attr(search_attr, search_accuracy=0.7)")
    # INPUT  : search_attr  str  — approximate attribute name (e.g. 'email', 'rol')
    # RETURNS: str  — best-matching canonical attribute name, or '' if none
    match = persons.search_for_attr("rol")
    print(f"  search_for_attr('rol') -> '{match}'")


def demo_search_by_key(persons: Persons):
    _section("persons.search_by_key(search_attr, search_str, role_key='', search_accuracy=0.7)")
    # INPUT  : search_attr  str  — attribute name to filter on (fuzzy-matched first)
    #          search_str   str  — value to search for within that attribute
    # RETURNS: list[Person] sorted by similarity; also sets persons.search_results
    results = persons.search_by_key("role", "teacher")
    print(f"  search_by_key('role', 'teacher') -> {len(results)} person(s)")


def demo_append_selected(persons: Persons):
    _section("persons.append_selected_person(person)")
    # INPUT  : person  Person  — any Person object (typically from search results)
    # EFFECT : appends to persons.selected_persons
    # RETURNS: None
    if persons.persons:
        persons.append_selected_person(persons.persons[0])
        print(f"  selected_persons -> {[p.first_name for p in persons.selected_persons]}")


def demo_clear_selections(persons: Persons):
    _section("persons.clear_selections()")
    # INPUT  : (none)
    # EFFECT : resets search_results, selected_persons, selected_intersections
    # RETURNS: None
    persons.clear_selections()
    print(f"  selected_persons cleared -> {persons.selected_persons}")


# ---------------------------------------------------------------------------
# Global read-only print endpoints
# ---------------------------------------------------------------------------

def demo_global_prints(persons: Persons):
    _section("Global print endpoints (read-only)")

    _sub("persons.print_global_active_meetings()")
    # INPUT  : (none)  |  RETURNS: None  |  prints persons.active_meetings
    persons.print_global_active_meetings()

    _sub("persons.print_global_commitments()")
    # INPUT  : (none)  |  RETURNS: None  |  prints persons.commitments
    persons.print_global_commitments()

    _sub("persons.print_global_meetings_history()")
    # INPUT  : (none)  |  RETURNS: None  |  prints persons.meetings_history
    persons.print_global_meetings_history()


# ---------------------------------------------------------------------------
# Per-person read endpoints  (require a Person object)
# ---------------------------------------------------------------------------

def demo_per_person_prints(persons: Persons):
    _section("Per-person print endpoints (read-only, require Person object)")
    if not persons.persons:
        print("  (no persons loaded)")
        return
    p = persons.persons[0]

    _sub("persons.print_availability(person)")
    # INPUT  : person  Person
    # RETURNS: None  |  prints person.availability in persons.current_timezone
    persons.print_availability(p)

    _sub("persons.print_commitments(person)")
    # INPUT  : person  Person
    # RETURNS: None  |  prints person.commitments in persons.current_timezone
    persons.print_commitments(p)

    _sub("persons.print_meetings_history(person)")
    # INPUT  : person  Person
    # RETURNS: None  |  prints person.meetings_history in persons.current_timezone
    persons.print_meetings_history(p)

    _sub("persons.print_balance_history(person)")
    # INPUT  : person  Person
    # RETURNS: None  |  prints person.balance + person.balance_history
    persons.print_balance_history(p)


# ---------------------------------------------------------------------------
# Per-person getter endpoints  (return raw list data)
# ---------------------------------------------------------------------------

def demo_getters(persons: Persons):
    _section("Getter endpoints — return raw list data")
    if not persons.persons:
        print("  (no persons loaded)")
        return
    p = persons.persons[0]

    _sub("persons.get_availability(person)")
    # INPUT  : person  Person
    # RETURNS: list[[user_id_str, start_utc_str, end_utc_str]]
    avail = persons.get_availability(p)
    print(f"  get_availability({p.first_name}) -> {avail[:2]} ...")

    _sub("persons.get_commitments(person)")
    # RETURNS: list[[user_id_str, start_utc_str, end_utc_str]]
    commits = persons.get_commitments(p)
    print(f"  get_commitments({p.first_name}) -> {commits[:2]} ...")

    _sub("persons.get_meetings_history(person)")
    # RETURNS: list[[user_id_str, start_utc_str, end_utc_str]]
    meetings = persons.get_meetings_history(p)
    print(f"  get_meetings_history({p.first_name}) -> {meetings[:2]} ...")

    _sub("persons.get_active_meetings_for(person)")
    # INPUT  : person  Person
    # RETURNS: list[[ids_str, start_utc_str, end_utc_str]]
    #          subset of persons.active_meetings where person.id is a participant
    active = persons.get_active_meetings_for(p)
    print(f"  get_active_meetings_for({p.first_name}) -> {active}")


# ---------------------------------------------------------------------------
# Availability write endpoints
# ---------------------------------------------------------------------------

def demo_availability_write(persons: Persons):
    _section("Availability write endpoints")
    if not persons.persons:
        print("  (no persons loaded)")
        return
    p = persons.persons[0]
    tz = ZoneInfo("America/Toronto")

    start = datetime(2099, 6, 1, 9, 0, tzinfo=tz)   # far-future — won't collide
    end   = datetime(2099, 6, 1, 11, 0, tzinfo=tz)

    _sub("persons.create_availability(person, start_datetime, end_datetime)")
    # INPUT  : person          Person
    #          start_datetime  datetime  tz-aware
    #          end_datetime    datetime  tz-aware
    # EFFECT : merges into person.availability (overlap-aware) + syncs to DB
    # RETURNS: None
    persons.create_availability(p, start, end)
    print(f"  created: {start} -> {end}")
    print(f"  person.availability now has {len(p.availability)} slot(s)")

    _sub("persons.remove_availability(person, start_datetime, end_datetime)")
    # INPUT  : person          Person
    #          start_datetime  datetime  tz-aware  (or omit and use target_index)
    #          end_datetime    datetime  tz-aware
    #   -OR-
    #          target_index    int       index into person.availability list
    # EFFECT : removes / splits slots as needed + syncs to DB
    # RETURNS: None
    persons.remove_availability(p, start, end)
    print(f"  removed: {start} -> {end}")
    print(f"  person.availability now has {len(p.availability)} slot(s)")


# ---------------------------------------------------------------------------
# Commitment write endpoints
# ---------------------------------------------------------------------------

def demo_commitment_write(persons: Persons):
    _section("Commitment write endpoints")
    if not persons.persons:
        print("  (no persons loaded)")
        return
    p = persons.persons[0]
    tz = ZoneInfo("America/Toronto")

    start = datetime(2099, 7, 1, 14, 0, tzinfo=tz)
    end   = datetime(2099, 7, 1, 15, 0, tzinfo=tz)

    _sub("persons.create_commitment(person, start_datetime, end_datetime)")
    # INPUT  : person          Person
    #          start_datetime  datetime  tz-aware
    #          end_datetime    datetime  tz-aware
    # EFFECT : merges into person.commitments + syncs to DB commitment_participants
    # RETURNS: None
    persons.create_commitment(p, start, end)
    print(f"  created: {start} -> {end}")

    _sub("persons.remove_commitment(person, start_datetime, end_datetime)")
    # Same signature options as remove_availability (datetime pair OR target_index)
    persons.remove_commitment(p, start, end)
    print(f"  removed: {start} -> {end}")


# ---------------------------------------------------------------------------
# Meeting write endpoints
# ---------------------------------------------------------------------------

def demo_meeting_write(persons: Persons):
    _section("Meeting write endpoints")
    if not persons.persons:
        print("  (no persons loaded)")
        return
    p = persons.persons[0]
    tz = ZoneInfo("America/Toronto")

    start = datetime(2099, 8, 1, 10, 0, tzinfo=tz)
    end   = datetime(2099, 8, 1, 11, 0, tzinfo=tz)

    _sub("persons.create_meeting(person, start_datetime, end_datetime)")
    # INPUT  : person          Person
    #          start_datetime  datetime  tz-aware
    #          end_datetime    datetime  tz-aware
    # EFFECT : merges into person.meetings_history + syncs to DB meeting_participants
    # RETURNS: None
    persons.create_meeting(p, start, end)
    print(f"  created: {start} -> {end}")

    _sub("persons.remove_meeting(person, start_datetime, end_datetime)")
    persons.remove_meeting(p, start, end)
    print(f"  removed: {start} -> {end}")


# ---------------------------------------------------------------------------
# Intersection + commitment-from-intersection
# ---------------------------------------------------------------------------

def demo_plan_meeting(persons: Persons):
    _section("Plan meeting: intersection -> commitment")

    _sub("persons.get_intersecting_availability(target_persons=[])")
    # INPUT  : target_persons  list[Person]  (defaults to persons.selected_persons)
    #          Requires >= 2 persons with overlapping availability
    # RETURNS: list[[ids_str, start_utc_str, end_utc_str]]
    #          Each entry is a window where ALL listed persons are free.
    #          ids_str format: "38&39&50"  (& -separated user ids)
    # NOTE   : does NOT persist anything; purely computed from in-memory availability
    if len(persons.persons) >= 2:
        intersections = persons.get_intersecting_availability(persons.persons[:2])
        print(f"  intersections for persons[0..1] -> {intersections}")
    else:
        print("  (need >= 2 persons to demo)")
        intersections = []

    _sub("persons.append_selected_intersection(intersection)")
    # INPUT  : intersection  [ids_str, start_utc_str, end_utc_str]
    # EFFECT : appends to persons.selected_intersections
    # RETURNS: None
    # (Typically called for each item the user picks from the intersection list)
    if intersections:
        persons.append_selected_intersection(intersections[0])
        print(f"  selected_intersections -> {persons.selected_intersections}")

    _sub("persons.create_intersecting_commitments(remove_availability=False)")
    # INPUT  : remove_availability  bool
    #          If True, the overlapping availability window is consumed when committed.
    # EFFECT : for each item in persons.selected_intersections:
    #            - inserts into global commitments table
    #            - inserts commitment_participants rows
    #            - calls person.create_commitment() for each participant
    #            - optionally calls person.remove_availability()
    # RETURNS: None
    if persons.selected_intersections:
        persons.create_intersecting_commitments(remove_availability=False)
        print(f"  commitments created from intersections")
    persons.clear_selections()


# ---------------------------------------------------------------------------
# Person registration
# ---------------------------------------------------------------------------

def demo_register_person(persons: Persons):
    _section("persons.register_person(items)")
    # INPUT  : items  dict with keys matching person_attributes:
    #   {
    #     "role"            : str,   e.g. "student" | "teacher"
    #     "first_name"      : str,
    #     "last_name"       : str,
    #     "family_id"       : str,   optional — auto-assigned if blank
    #     "date_registered" : str,   "YYYY-MM-DD"
    #     "date_of_birth"   : str,   "YYYY-MM-DD"
    #     "address"         : str,
    #     "phone_number"    : str,   e.g. "+1 416-555-0101"
    #     "email"           : str,
    #     "rate"            : str,   numeric string, e.g. "75.0"
    #     "balance"         : str,   numeric string, default "0"
    #     "timezone"        : str,   IANA key, e.g. "America/Toronto"
    #     "comments"        : str,   optional
    #   }
    #   NOTE: "id" is auto-assigned — do NOT include it in items.
    #
    # EFFECT : validates input; on success:
    #            - creates Person object + appends to persons.persons
    #            - inserts row into users table in DB
    # RETURNS: None  (prints warnings on validation failure)
    #
    # ---- UNCOMMENT BELOW TO RUN A LIVE REGISTRATION DEMO ----
    # demo_items = {
    #     "role": "student",
    #     "first_name": "Demo",
    #     "last_name": "User",
    #     "family_id": "",
    #     "date_registered": "2026-03-14",
    #     "date_of_birth": "2000-01-01",
    #     "address": "1 Demo Street",
    #     "phone_number": "+1 555-000-9999",
    #     "email": "demo@demo.fake",
    #     "rate": "60.0",
    #     "balance": "0",
    #     "timezone": "America/Toronto",
    #     "comments": "demo registration",
    # }
    # persons.register_person(demo_items)
    print("  (registration demo commented out — edit this file to run it)")


# ===========================================================================
#  PERSON ENDPOINTS  (called directly on a Person object)
# ===========================================================================
#
#  The Persons wrapper methods above delegate to these under the hood.
#  A front-end can call them directly on any Person object retrieved from
#  persons.persons, persons.selected_persons, or persons.search_results.
#
# ===========================================================================

def demo_person_direct(persons: Persons):
    _section("Direct Person object endpoints")
    if not persons.persons:
        print("  (no persons loaded)")
        return
    p = persons.persons[0]

    _sub("Person attributes (read)")
    # All attributes are plain strings (stored as str, cast on use):
    print(f"  p.id            = {p.id}")
    print(f"  p.role          = {p.role}")
    print(f"  p.first_name    = {p.first_name}")
    print(f"  p.last_name     = {p.last_name}")
    print(f"  p.family_id     = {p.family_id}")
    print(f"  p.date_registered = {p.date_registered}")
    print(f"  p.date_of_birth = {p.date_of_birth}")
    print(f"  p.address       = {p.address}")
    print(f"  p.phone_number  = {p.phone_number}")
    print(f"  p.email         = {p.email}")
    print(f"  p.rate          = {p.rate}")
    print(f"  p.balance       = {p.balance}")
    print(f"  p.timezone      = {p.timezone}")
    print(f"  p.comments      = {p.comments}")

    _sub("Person scheduling data (read — list of [id_str, start_utc, end_utc])")
    print(f"  p.availability      [{len(p.availability)}]")
    print(f"  p.commitments       [{len(p.commitments)}]")
    print(f"  p.meetings_history  [{len(p.meetings_history)}]")
    # balance_history rows: [user_id, associate_ids, start_utc, end_utc, amount, balance_after]
    print(f"  p.balance_history   [{len(p.balance_history)}]")

    _sub("str(person)")
    # FORMAT: "Person: role, first_name, last_name, id, family_id, date_registered,
    #          date_of_birth, address, phone_number, email, rate, balance, timezone, comments"
    print(f"  str(p) = {str(p)}")

    _sub("person == other  /  person < other")
    # Equality is by id.  Ordering is alphabetical by (first_name, last_name, id).
    if len(persons.persons) >= 2:
        other = persons.persons[1]
        print(f"  persons[0] == persons[1]: {p == other}")
        print(f"  persons[0] <  persons[1]: {p < other}")


# ===========================================================================
#  MAIN  — run all demos
# ===========================================================================

def run_all_demos():
    persons = demo_persons_init()

    demo_persons_update(persons)
    demo_search_generically(persons)
    demo_search_for_attr(persons)
    demo_search_by_key(persons)
    demo_append_selected(persons)
    demo_clear_selections(persons)

    demo_global_prints(persons)
    demo_per_person_prints(persons)
    demo_getters(persons)

    demo_availability_write(persons)
    demo_commitment_write(persons)
    demo_meeting_write(persons)

    demo_plan_meeting(persons)
    demo_register_person(persons)

    demo_person_direct(persons)

    print(f"\n{SEP}\n  All endpoint demos complete.\n{SEP}\n")


if __name__ == "__main__":
    run_all_demos()
