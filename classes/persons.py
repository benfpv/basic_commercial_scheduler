
import difflib
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from copy import deepcopy

from classes.person import *
from db import database

class Persons():
    def __init__(self, current_timezone=None):
        """
        Persons creates, stores, and operates on a collection of Person objects.
        Intended to be all-in-one structure containing all person objects, but only loading/writing as needed per operation.
        Methods (high-level summary):
        - search for & store specific persons in working memory to operate on.
        - print/create/infer/save scheduling variables (e.g., availabilities, commitments, meetings)
        """
        ### Static (or LTM) Variables ###
        # Debug Outputs
        self.print_debug = False
        Person.print_debug = self.print_debug
        # Initialise database (creates data_pilot/scheduler.db if not present)
        database.init_db()
        ### Global Scheduling Data (all persons, loaded from DB) ###
        _commitment_rows = database.fetch_all(
            """SELECT GROUP_CONCAT(cp.user_id, '&') AS ids, c.start_utc, c.end_utc
               FROM commitments c
               JOIN commitment_participants cp ON c.commitment_id = cp.commitment_id
               WHERE NOT EXISTS (
                   SELECT 1 FROM meetings m WHERE m.commitment_id = c.commitment_id
               )
               GROUP BY c.commitment_id
               ORDER BY c.start_utc"""
        )
        self.commitments = [[r["ids"], r["start_utc"], r["end_utc"]] for r in _commitment_rows]
        _meetings_history_rows = database.fetch_all(
            """SELECT GROUP_CONCAT(mp.user_id, '&') AS ids, m.start_utc, m.end_utc
               FROM meetings m
               JOIN meeting_participants mp ON m.meeting_id = mp.meeting_id
               GROUP BY m.meeting_id
               ORDER BY m.start_utc"""
        )
        self.meetings_history = [[r["ids"], r["start_utc"], r["end_utc"]] for r in _meetings_history_rows]
        # Import Persons from DB
        _user_rows = database.fetch_all("SELECT * FROM users ORDER BY id")
        persons_lines = [
            [str(r["role"]), str(r["first_name"]), str(r["last_name"]),
             str(r["id"]), str(r["family_id"]), str(r["date_registered"]),
             str(r["date_of_birth"]), str(r["address"] or ""),
             str(r["phone_number"] or ""), str(r["email"] or ""),
             str(r["rate"]), str(r["balance"]), str(r["timezone"]),
             str(r["comments"] or "")]
            for r in _user_rows
        ]
        self.person_attributes = ["role", "first_name", "last_name", "id", "family_id",
                                   "date_registered", "date_of_birth", "address",
                                   "phone_number", "email", "rate", "balance",
                                   "timezone", "comments"]
        self.persons_len, self.persons = self._create_persons(
            self.person_attributes, len(persons_lines), persons_lines
        )
        # Balance Entry Modifiers (e.g., events, discounts)
        self.global_balance_entry_modifiers = [] # list of floats that will be summed up (e.g., 1.0 is regular price).
        
        ### Global Working Memory (computed at runtime, not persisted) ###
        # Datetime
        self.current_timezone = ZoneInfo(current_timezone) if (current_timezone) else datetime.now().astimezone().tzinfo
        self.current_datetime = datetime.now(self.current_timezone)
        # Global: active meetings (commitments whose window straddles now — transient, recomputed each update)
        self.active_meetings = []
        # Admin working memory
        self.search_results = []
        self.selected_persons = []
        self.selected_intersections = []
        
    def __str__(self):
        string = f"Persons [{self.persons_len}]: {[x.first_name for x in self.persons]}"
        return string
    
    def _update_current_datetime(self):
        print(f"------ _update_current_datetime() ------") if (self.print_debug == True) else False
        prev_datetime = deepcopy(self.current_datetime)
        self.current_datetime = datetime.now(self.current_timezone)
        print(f"- Datetime Updated: {prev_datetime} -> {self.current_datetime}")
        
    def update(self):
        print(f"------ update() ------") if (self.print_debug == True) else False
        self._update_current_datetime()
        self.update_commitments_to_meetings()
    
    def _validate_user(self, items, persons):
        print(f"------ _validate_user() ------") if (self.print_debug == True) else False
        errors = []
        items = {k: str(v) if v is not None else "" for k, v in items.items()}
        required_fields = ["role", "first_name", "last_name", "date_registered", "date_of_birth", "address", "phone_number", "email", "rate", "timezone"]
        for field in required_fields:
            if items.get(field, "").strip() == "":
                errors.append(f"{field.replace('_', ' ').title()} is missing")
        email = items.get("email", "")
        if email and ("@" not in email or "." not in email):
            errors.append("Email format is invalid")
        phone_number = items.get("phone_number", "")
        if phone_number:
            digits_only = "".join(c for c in phone_number if c.isdigit())
            if len(digits_only) < 7:
                errors.append("Phone number seems too short")
        rate = items.get("rate", "")
        try:
            r = float(rate)
            if r < 0:
                errors.append("Rate cannot be negative")
        except:
            errors.append("Rate must be a number")
        balance = items.get("balance", "0")
        if balance:
            try:
                float(balance)
            except:
                errors.append("Balance must be a number")
        for date_field, name in [("date_registered", "Date Registered"), ("date_of_birth", "Date of Birth")]:
            date_value = items.get(date_field, "")
            parts = date_value.split("-")
            if len(parts) != 3 or not all(p.isdigit() for p in parts):
                errors.append(f"{name} must be in YYYY-MM-DD format")
            else:
                try:
                    d = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
                    if date_field == "date_of_birth" and d.date() >= datetime.today().date():
                        errors.append("Date of Birth must be in the past")
                    if date_field == "date_registered" and d.date() > datetime.today().date():
                        errors.append("Date Registered cannot be in the future")
                except:
                    errors.append(f"{name} is not a valid date")
        id_str = items.get("id", "")
        family_id_str = items.get("family_id", "")
        for person in persons:
            if hasattr(person, "email") and str(person.email) == email:
                errors.append("A user with this email already exists")
            if hasattr(person, "phone_number") and str(person.phone_number) == phone_number:
                errors.append("A user with this phone number already exists")
            if id_str and hasattr(person, "id") and str(person.id) == id_str:
                errors.append("This User ID is already taken")
            if family_id_str and hasattr(person, "family_id") and str(person.family_id) == family_id_str:
                errors.append("This Family ID is already used")
        if items.get("timezone", "").strip() == "":
            errors.append("Timezone is missing")
        if errors:
            print("=== Errors Found ===")
            for error in errors:
                print("-", error)
            return False
        return True

    def _create_persons(self, persons_header, persons_lines_len, persons_lines):
        print(f"------ create_persons() ------") if (self.print_debug == True) else False
        persons = []
        for i, s in enumerate(persons_lines):
            person = Person(s)
            print(f"[{i+1}]: {person}") if (self.print_debug == True) else False
            persons.append(person)
        persons_len = len(persons)
        return persons_len, persons
        
    def register_person(self, items):
        print(f"------ register_person() ------") if self.print_debug else False
        # Generate User ID
        ids = [int(x.id) for x in self.persons]
        new_id = 0
        while new_id in ids:
            new_id += 1
        items["id"] = str(new_id)
        # Generate Family ID if not provided
        if not items.get("family_id"):
            family_ids = [int(x.family_id) for x in self.persons]
            new_family_id = 0
            while new_family_id in family_ids:
                new_family_id += 1
            items["family_id"] = str(new_family_id)
        # Validate user information
        user_is_valid = self._validate_user(items, self.persons)
        if user_is_valid:
            # Convert dict to ordered list to match Person() __init__
            items_list = [
                items["role"],
                items["first_name"],
                items["last_name"],
                items["id"],
                items["family_id"],
                items["date_registered"],
                items["date_of_birth"],
                items["address"],
                items["phone_number"],
                items["email"],
                items["rate"],
                items.get("balance", "0"),
                items["timezone"],
                items.get("comments", "")
            ]
            # Create the person object and append to the list
            person = Person(items_list)
            self.persons.append(person)
            self.persons_len = len(self.persons)
            database.execute(
                """INSERT OR IGNORE INTO users
                   (id, role, first_name, last_name, family_id, date_registered,
                    date_of_birth, address, phone_number, email, rate, balance,
                    timezone, comments)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (int(items["id"]), items["role"], items["first_name"], items["last_name"],
                 int(items.get("family_id", 0)), items["date_registered"],
                 items["date_of_birth"], items["address"], items["phone_number"],
                 items["email"], float(items["rate"]), float(items.get("balance", "0")),
                 items["timezone"], items.get("comments", ""))
            )
            if self.print_debug:
                print(f"Person registered with ID {new_id}")
        else:
            print("WARNING: Person NOT Registered!")
        return

    def _sort_datetimes_by_start_datetime(self, datetimes_list):
        print(f"------ _sort_datetimes_by_start_datetime() ------") if (self.print_debug == True) else False
        start_datetime_index = 1
        datetimes_list.sort(key=lambda d: d[1])
        
    def search_generically(self, search_str, role_key="", search_accuracy=0.7):
        """
        inputs:
            search_str: the string we are searching each attribute for (str).
        returns:
            matched: a list of persons who share the memory addresses* of self.persons, thus if they are changed, actual self.persons are changed as well.
        """
        print(f"------ search_generically() for '{search_str}' ------") if (self.print_debug == True) else False
        search_words = search_str.lower().split(" ")
        matched = []
        role_specific_persons = [x for x in self.persons if (role_key in x.role)] if role_key else self.persons
        for person in role_specific_persons:
            person_values = [v.lower() for v in vars(person).values() if isinstance(v, str)]
            word_scores = []
            for word in search_words:
                best_word_ratio = max(difflib.SequenceMatcher(None, word, val).ratio() for val in person_values)
                word_scores.append(best_word_ratio)
            final_score = sum(word_scores) / len(word_scores)
            if final_score >= search_accuracy:
                matched.append((person, final_score))
        matched.sort(key=lambda x: x[1], reverse=True)
        matched = [s for s, r in matched]
        matched_len = len(matched)
        print(f"Matched Persons [{matched_len}]: ") if (self.print_debug == True) else False
        [print(f"- {x}") for x in matched] if (self.print_debug == True) else False
        self.search_results = matched
        return matched

    def search_for_attr(self, search_attr, search_accuracy=0.7):
        print(f"------ search_for_attr() for '{search_attr}'------") if (self.print_debug == True) else False
        matches = difflib.get_close_matches(search_attr.lower(), self.person_attributes, n=1, cutoff=search_accuracy)
        if (not matches):
            print(f"- Attribute '{search_attr}' not found!")
        else:
            matches = matches[0]
            print(f"- Attribute '{search_attr}' found as '{matches}'!")
        return matches

    def search_by_key(self, search_attr, search_str, role_key="", search_accuracy=0.7):
        """
        inputs:
            search_attr: the only attribute we want to consider when searching for search_str (str).
            search_str: the string we are searching each attribute for (str).
        returns:
            matched_persons: a list of persons who share the memory addresses* of self.persons, thus if they are changed, actual self.persons are changed as well.
        """
        print(f"------ search_by_key() for '{search_attr}' == '{search_str}' ------") if (self.print_debug == True) else False
        matched = []
        if (role_key):
            role_specific_persons = [x for x in self.persons if (role_key in x.role)]
        else:
            role_specific_persons = self.persons
            matched_attr_head = self.search_for_attr(search_attr)
            if (matched_attr_head):
                for person in role_specific_persons:
                    person_values = [v.lower() for x,v in vars(person).items() if (x == matched_attr_head)]
                    match_attr = difflib.get_close_matches(search_str.lower(), person_values, n=1, cutoff=search_accuracy)
                    if (match_attr):
                        best_ratio = max(difflib.SequenceMatcher(None, search_str.lower(), val).ratio() for val in person_values)
                        matched.append((person, best_ratio))
                # Sort persons by similarity (highest first)
                matched.sort(key=lambda x: x[1], reverse=True)
                # If you want just the person objects
                matched = [s for s, ratio in matched]
                matched_len = len(matched)
                print(f"Matched Persons [{matched_len}]: ") if (self.print_debug == True) else False
                [print(f"- {x}") for x in matched] if (self.print_debug == True) else False
                self.search_results = matched
        return matched
    
    def print_global_active_meetings(self):
        print(f"------ print_global_active_meetings() ------") if (self.print_debug == True) else False
        print(f"Global Active Meetings: [{len(self.active_meetings)}]: ")
        if self.active_meetings:
            [print(f"- {x}") for x in self.active_meetings]
        else:
            print("- (none)")
    def get_active_meetings_for(self, person):
        """Returns active meetings relevant to this person (filtered from global active_meetings)."""
        return [m for m in self.active_meetings if person.id in m[0].split("&")]
    def print_global_commitments(self):
        print(f"------ print_global_commitments() ------") if (self.print_debug == True) else False
        print(f"Global Commitments [{len(self.commitments)}]: ")
        if self.commitments:
            [print(f"- {x}") for x in self.commitments]
        else:
            print("- (none)")
    def print_global_meetings_history(self):
        print(f"------ print_global_meetings_history() ------") if (self.print_debug == True) else False
        print(f"Global Meetings History [{len(self.meetings_history)}]: ")
        if self.meetings_history:
            [print(f"- {x}") for x in self.meetings_history]
        else:
            print("- (none)")
        
    def clear_selections(self):
        print(f"------ clear_selections() ------") if (self.print_debug == True) else False
        self.search_results = []
        self.selected_persons = []
        self.selected_intersections = []
            
    def print_selected_persons(self):
        print(f"------ print_selected_persons() ------") if (self.print_debug == True) else False
        print(f"Selected Persons [{len(self.selected_persons)}]: ")
        if self.selected_persons:
            [print(f"- {x}") for x in self.selected_persons]
        else:
            print("- (none)")
    def append_selected_person(self, person):
        print(f"------ append_selected_person() ------") if (self.print_debug == True) else False
        self.selected_persons.append(person)
        
    def append_selected_intersection(self, intersection):
        print(f"------ append_selected_intersection() ------") if (self.print_debug == True) else False
        self.selected_intersections.append(intersection)
        
    def print_availability(self, person):
        FMT = "%Y-%m-%d %H:%M:%S%z"
        print(f"------ print_availability() for '{person}' ------") if (self.print_debug == True) else False
        print(person)
        print(f"Availability [{len(person.availability)}] (Timezone: {self.current_timezone}): ")
        if person.availability:
            for x in person.availability:
                start_datetime = datetime.strptime(x[1], FMT).astimezone(self.current_timezone)
                end_datetime = datetime.strptime(x[2], FMT).astimezone(self.current_timezone)
                print(f"- {start_datetime} -> {end_datetime}")
        else:
            print("- (none)")
    def create_availability(self, person, start_datetime, end_datetime):
        print(f"------ create_availability() for '{person}' ------") if (self.print_debug == True) else False
        person.create_availability(start_datetime, end_datetime)
    def get_availability(self, person):
        print(f"------ get_availability() for '{person}' ------") if (self.print_debug == True) else False
        return person.availability
    def remove_availability(self, person, start_datetime="", end_datetime="", target_index=None):
        print(f"------ remove_availability() for '{person}' ------") if (self.print_debug == True) else False
        person.remove_availability(start_datetime, end_datetime, target_index)
    
    def print_commitments(self, person):
        FMT = "%Y-%m-%d %H:%M:%S%z"
        print(f"------ print_commitments() for '{person}' ------") if (self.print_debug == True) else False
        print(person)
        print(f"Commitments [{len(person.commitments)}] (Timezone: {self.current_timezone}): ")
        if person.commitments:
            for x in person.commitments:
                start_datetime = datetime.strptime(x[1], FMT).astimezone(self.current_timezone)
                end_datetime = datetime.strptime(x[2], FMT).astimezone(self.current_timezone)
                print(f"- {start_datetime} -> {end_datetime}")
        else:
            print("- (none)")
    def create_commitment(self, person, start_datetime, end_datetime):
        print(f"------ create_commitment() for '{person}' ------") if (self.print_debug == True) else False
        person.create_commitment(start_datetime, end_datetime)
    def get_commitments(self, person):
        print(f"------ get_commitments() for '{person}' ------") if (self.print_debug == True) else False
        return person.commitments
    def remove_commitment(self, person, start_datetime="", end_datetime="", target_index=None):
        print(f"------ remove_commitment() for '{person}' ------") if (self.print_debug == True) else False
        person.remove_commitment(start_datetime, end_datetime, target_index)
    
    def print_meetings_history(self, person):
        FMT = "%Y-%m-%d %H:%M:%S%z"
        print(f"------ print_meetings_history() for '{person}' ------") if (self.print_debug == True) else False
        print(person)
        print(f"Meetings History [{len(person.meetings_history)}] (Timezone: {self.current_timezone}): ")
        if person.meetings_history:
            for x in person.meetings_history:
                start_datetime = datetime.strptime(x[1], FMT).astimezone(self.current_timezone)
                end_datetime = datetime.strptime(x[2], FMT).astimezone(self.current_timezone)
                print(f"- {start_datetime} -> {end_datetime}")
        else:
            print("- (none)")
    def create_meeting(self, person, start_datetime, end_datetime):
        print(f"------ create_meeting() for '{person}' ------") if (self.print_debug == True) else False
        person.create_meeting(start_datetime, end_datetime)
    def get_meetings_history(self, person):
        print(f"------ get_meetings_history() for '{person}' ------") if (self.print_debug == True) else False
        return person.meetings_history
    def remove_meeting(self, person, start_datetime="", end_datetime="", target_index=None):
        print(f"------ remove_meeting() for '{person}' ------") if (self.print_debug == True) else False
        person.remove_meeting(start_datetime, end_datetime, target_index)
    def print_balance_history(self, person):
        print(f"------ print_balance_history() for '{person}' ------") if (self.print_debug == True) else False
        person.print_balance_history()

    def get_intersecting_availability(self, target_persons=[]):
        FMT = "%Y-%m-%d %H:%M:%S%z"
        print(f"------ get_intersecting_availability() ------") if (self.print_debug == True) else False
        if (not target_persons):
            target_persons = self.selected_persons
        target_persons_len = len(target_persons)
        availabilities = []
        intersections = []
        if (target_persons_len > 1):
            for i, person in enumerate(target_persons):
                availability = person.availability
                availabilities.append(availability)
                print(f"Availability {i+1}/{target_persons_len} [{len(availability)}]: {availability}") if (self.print_debug == True) else False
            intersections = availabilities[0]
            for next_availability in availabilities[1:]:
                this_intersections = []
                for cid, c_start, c_end in intersections:
                    c_start_dt = datetime.strptime(c_start, FMT)
                    c_end_dt = datetime.strptime(c_end, FMT)
                    for nid, n_start, n_end in next_availability:
                        n_start_dt = datetime.strptime(n_start, FMT)
                        n_end_dt = datetime.strptime(n_end, FMT)
                        start = max(c_start_dt, n_start_dt)
                        end = min(c_end_dt, n_end_dt)
                        if start < end:
                            this_intersections.append([f"{cid}&{nid}", start.isoformat(sep=" "), end.isoformat(sep=" ")])
                # Move forward with the new this_intersections
                intersections = this_intersections
                # Early exit if nothing overlaps anymore
                if not intersections:
                    break
            print(f"Availability Intersections [{len(intersections)}]: {intersections}") if (self.print_debug == True) else False
            self.selected_intersections = []
        return intersections
        
    def _process_write_datetimes(self, source_datetimes_list, target_datetimes_working_memory, sort_working_memory=True):
        print(f"------ _process_write_datetimes() ------") if (self.print_debug == True) else False
        for i, this_datetime in enumerate(source_datetimes_list):
            print(f"Datetime {i+1}/{len(source_datetimes_list)}: {this_datetime}") if (self.print_debug == True) else False
            if (this_datetime not in target_datetimes_working_memory):
                target_datetimes_working_memory.append(this_datetime)
                print(f"- Datetime Created: {this_datetime}") if (self.print_debug == True) else False
            else:
                print(f"- Datetime Already Exists (Not Created): {this_datetime}") if (self.print_debug == True) else False
        if (sort_working_memory):
            self._sort_datetimes_by_start_datetime(target_datetimes_working_memory)
        
    def create_intersecting_commitments(self, remove_availability=False):
        FMT = "%Y-%m-%d %H:%M:%S%z"
        print(f"------ create_intersecting_commitments() ------") if (self.print_debug == True) else False
        # Create Global Commitments
        self._process_write_datetimes(self.selected_intersections, self.commitments)
        # Sync new commitments to DB (dual-write)
        for intersection in self.selected_intersections:
            ids_str, start_utc, end_utc = intersection[0], intersection[1], intersection[2]
            if not database.fetch_one(
                "SELECT commitment_id FROM commitments WHERE start_utc=? AND end_utc=?",
                (start_utc, end_utc)
            ):
                commitment_id = database.insert(
                    "INSERT INTO commitments (start_utc, end_utc) VALUES (?,?)",
                    (start_utc, end_utc)
                )
                for uid in ids_str.split("&"):
                    database.execute(
                        "INSERT OR IGNORE INTO commitment_participants (commitment_id, user_id) VALUES (?,?)",
                        (commitment_id, int(uid.strip()))
                    )
        
        # Create Person-Wise Commitments
        intersections_len = len(self.selected_intersections)
        for i, intersection in enumerate(self.selected_intersections):
            print(f"Intersection {i+1}/{intersections_len}: {intersection}") if (self.print_debug == True) else False
            id_index = 0
            datetime_start_index = 1
            datetime_end_index = 2
            
            intersection_ids = [x for x in intersection[id_index].split("&")]
            intersection_ids_len = len(intersection_ids)
            
            datetime_start_utc = datetime.strptime(intersection[datetime_start_index], FMT)
            datetime_end_utc = datetime.strptime(intersection[datetime_end_index], FMT)
            
            # Obtain only relevant target persons
            target_persons = [x for x in self.persons if (x.id in intersection_ids)]
            target_persons_len = len(target_persons)
            
            # Create Commitment at Person Object level
            for i, person in enumerate(target_persons):
                # Redundant Check/Query for Matching ID
                print(f"- Matching ID ({person.id} in {intersection_ids})?: {person.id in intersection_ids}") if (self.print_debug == True) else False
                
                availability = deepcopy(person.availability)
                commitments = deepcopy(person.commitments)
                
                person.create_commitment(datetime_start_utc, datetime_end_utc)
                
                if (remove_availability):
                    person.remove_availability(datetime_start_utc, datetime_end_utc)
                
                print(f"------ (return to) create_intersecting_commitments() ------") if (self.print_debug == True) else False
                print(f"- Availability (Before) {i+1}/{target_persons_len} [{len(availability)}]: {availability}") if (self.print_debug == True) else False
                print(f"- Commitments (Before) {i+1}/{target_persons_len} [{len(commitments)}]: {commitments}") if (self.print_debug == True) else False
                
                availability = person.availability
                commitments = person.commitments
                
                print(f"- Availability (After) {i+1}/{target_persons_len} [{len(availability)}]: {availability}") if (self.print_debug == True) else False
                print(f"- Commitments (After) {i+1}/{target_persons_len} [{len(commitments)}]: {commitments}") if (self.print_debug == True) else False
        
        self.print_global_commitments()
        return
        
    def _create_balance_entries(self, meeting):
        FMT = "%Y-%m-%d %H:%M:%S%z"
        print(f"------ _create_balance_entries() ------") if (self.print_debug == True) else False
        print(f"Meeting: {meeting}") if (self.print_debug == True) else False
        id_index = 0
        datetime_start_index = 1
        datetime_end_index = 2
        
        meeting_ids_str = meeting[id_index]
        meeting_ids = [x for x in meeting[id_index].split("&")]
        meeting_ids_len = len(meeting_ids)
        
        start_time_utc = meeting[datetime_start_index]
        end_time_utc = meeting[datetime_end_index]
        
        # Obtain only relevant target persons
        target_persons = [x for x in self.persons if (x.id in meeting_ids)]
        target_persons_len = len(target_persons)
            
        for i, target_person in enumerate(target_persons):
            entry = float(target_person.rate)
            for em in self.global_balance_entry_modifiers:
                entry *= float(em)
            target_person.create_balance_entry(meeting_ids_str, start_time_utc, end_time_utc, entry)
        
    def _postprocess_meeting(self, meeting):
        print(f"------ _postprocess_meeting() ------") if (self.print_debug == True) else False
        self._create_balance_entries(meeting)
    
    def update_commitments_to_meetings(self, remove_availability=False, remove_commitment=True):
        FMT = "%Y-%m-%d %H:%M:%S%z"
        print(f"------ update_commitments_to_meetings() ------") if (self.print_debug == True) else False
        
        ### Gather evidence whether the meeting occurred; who attended, etc.
        # By Datetime Crossover Current Datetime
        active_meetings = [] # Currently in session
        crossedover = [] # Simply the current datetime has crossed over commmitment start time
        commitments_len = len(self.commitments)
        for i, commitment in enumerate(self.commitments):
            print(f"Commitment {i+1}/{commitments_len}: {commitment}") if (self.print_debug == True) else False
            id_index = 0
            datetime_start_index = 1
            datetime_end_index = 2
            
            intersection_ids = [x for x in commitment[id_index].split("&")]
            intersection_ids_len = len(intersection_ids)
            
            datetime_start_utc = datetime.strptime(commitment[datetime_start_index], FMT)
            datetime_end_utc = datetime.strptime(commitment[datetime_end_index], FMT)
            
            if (datetime_start_utc <= self.current_datetime <= datetime_end_utc):
                active_meetings.append(deepcopy(commitment))
            if (datetime_start_utc <= self.current_datetime) and (datetime_end_utc < self.current_datetime):
                crossedover.append(deepcopy(commitment))
        
        active_meetings_len = len(active_meetings)
        print(f"Meetings Detected Active [{active_meetings_len}]: ") if (self.print_debug == True) else False
        [print(x) for x in active_meetings] if (self.print_debug == True) else False
        crossedover_len = len(crossedover)
        print(f"Meetings Detected Crossed-Over [{crossedover_len}]: ") if (self.print_debug == True) else False
        [print(x) for x in crossedover] if (self.print_debug == True) else False
        
        ### Process Active Meetings (clear stale entries, then write fresh)
        self.active_meetings.clear()
        self._process_write_datetimes(active_meetings, self.active_meetings)
        
        ### Process Crossed Over (Filter Out Identicals)
        self._process_write_datetimes(crossedover, self.meetings_history)
        # Sync crossed-over meetings to DB (dual-write)
        # attended=1 for all participants: consistent with current behaviour where
        # time-crossover is the sole evidence of the meeting having occurred.
        for crossover in crossedover:
            ids_str, start_utc, end_utc = crossover[0], crossover[1], crossover[2]
            if not database.fetch_one(
                "SELECT meeting_id FROM meetings WHERE start_utc=? AND end_utc=?",
                (start_utc, end_utc)
            ):
                commitment_row = database.fetch_one(
                    "SELECT commitment_id FROM commitments WHERE start_utc=? AND end_utc=?",
                    (start_utc, end_utc)
                )
                commitment_id = commitment_row["commitment_id"] if commitment_row else None
                meeting_id = database.insert(
                    "INSERT INTO meetings (commitment_id, start_utc, end_utc) VALUES (?,?,?)",
                    (commitment_id, start_utc, end_utc)
                )
                for uid in ids_str.split("&"):
                    database.execute(
                        "INSERT OR IGNORE INTO meeting_participants (meeting_id, user_id, attended) VALUES (?,?,1)",
                        (meeting_id, int(uid.strip()))
                    )
        
        # Remove promoted commitments from in-memory global list
        # (DB rows are retained as audit trail; meetings.commitment_id links back to them)
        self.commitments[:] = [c for c in self.commitments if c not in crossedover]
        
        # Create Person-Wise Meetings
        for i, crossover in enumerate(crossedover):
            print(f"Crossover {i+1}/{crossedover_len}: {crossover}") if (self.print_debug == True) else False
            id_index = 0
            datetime_start_index = 1
            datetime_end_index = 2
            
            crossover_ids = [x for x in crossover[id_index].split("&")]
            crossover_ids_len = len(crossover_ids)
            
            datetime_start_utc = datetime.strptime(crossover[datetime_start_index], FMT)
            datetime_end_utc = datetime.strptime(crossover[datetime_end_index], FMT)
            
            # Obtain only relevant target persons
            target_persons = [x for x in self.persons if (x.id in crossover_ids)]
            target_persons_len = len(target_persons)
            
            # Create Commitment at Person Object level
            for i, person in enumerate(target_persons):
                # Redundant Check/Query for Matching ID
                print(f"- Matching ID ({person.id} in {crossover_ids})?: {person.id in crossover_ids}") if (self.print_debug == True) else False
                
                availability = deepcopy(person.availability)
                commitments = deepcopy(person.commitments)
                meetings = deepcopy(person.meetings_history)
                
                person.create_meeting(datetime_start_utc, datetime_end_utc)
                
                if (remove_availability):
                    person.remove_availability(datetime_start_utc, datetime_end_utc)
                if (remove_commitment):
                    person.remove_commitment(datetime_start_utc, datetime_end_utc)
                
                print(f"------ (return to) update_commitments_to_meetings() ------") if (self.print_debug == True) else False
                print(f"- Availability (Before) {i+1}/{target_persons_len} [{len(availability)}]: {availability}") if (self.print_debug == True) else False
                print(f"- Commitments (Before) {i+1}/{target_persons_len} [{len(commitments)}]: {commitments}") if (self.print_debug == True) else False
                print(f"- Meetings (Before) {i+1}/{target_persons_len} [{len(meetings)}]: {meetings}") if (self.print_debug == True) else False
                
                availability = person.availability
                commitments = person.commitments
                meetings = person.meetings_history
                
                print(f"- Availability (After) {i+1}/{target_persons_len} [{len(availability)}]: {availability}") if (self.print_debug == True) else False
                print(f"- Commitments (After) {i+1}/{target_persons_len} [{len(commitments)}]: {commitments}") if (self.print_debug == True) else False
                print(f"- Meetings (After) {i+1}/{target_persons_len} [{len(meetings)}]: {meetings}") if (self.print_debug == True) else False
                
            # Postprocess Meeting
            self._postprocess_meeting(crossover)
            
        self.print_global_commitments()
        self.print_global_meetings_history()
        return
        