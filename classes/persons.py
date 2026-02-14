
import os
import tempfile
import difflib
from datetime import datetime
from zoneinfo import ZoneInfo
from copy import deepcopy

from functions_csv import *

class Persons():
    def __init__(self, path_to_global_commitments_data, path_to_global_meetings_data, path_to_person_data, path_to_person_availability_data, path_to_person_commitments_data):
        """
        Persons creates, stores, and operates on a collection of Person objects.
        Intended to be all-in-one structure containing all person objects, but only loading/writing as needed per operation.
        Methods (high-level summary):
        - search for & store specific persons in working memory to operate on.
        - print/create/infer/save scheduling variables (e.g., availabilities, commitments, meetings)
        """
        ### Static Variables ###
        self.path_to_global_commitments_data = path_to_global_commitments_data
        
        Person.path_to_person_data = path_to_person_data
        Person.path_to_person_availability_data = path_to_person_availability_data
        Person.path_to_person_commitments_data = path_to_person_commitments_data
        
        persons_header, persons_lines_len, persons_lines = Functions_Csv.import_csv_cleaned(path_to_person_data)
        self.persons_len, self.persons = self._create_persons(persons_header, persons_lines_len, persons_lines)
        
        # Load Global Data (e.g., Commitments, Lessons History, Balance History)
        self.commitments = self._load_global_data(self.path_to_global_commitments_data)
        self.meetings = self._load_global_data(self.path_to_global_commitments_data)
        
        ### Dynamic Variables / Working Memories ###
        self.search_results = [] # one or more persons (i.e., person objects) are stored here after any search method.
        self.selected = [] # selected users are stored here as necessary so they can be operated on using inherent functions.
        self.selected_intersections = [] # intersections working memory
        
        ### Private Variables ###
        self._person_attributes = [x for x in persons_header]
        
    def __str__(self):
        string = f"Persons [{self.persons_len}]: {[x.first_name for x in self.persons]}"
        return string
    
    def _validate_user(self, items, persons):
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
        print_debug = True
        print(f"------ create_persons() ------") if (print_debug == True) else False
        persons = []
        for i, s in enumerate(persons_lines):
            person = Person(s)
            print(f"[{i+1}]: {person}") if (print_debug == True) else False
            persons.append(person)
        persons_len = len(persons)
        return persons_len, persons
        
    def register_person(self, items):
        print_debug = True
        print(f"------ register_person() ------") if print_debug else False
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
        # Print items for debugging
        print("Items to be registered:", items)  # Add this line to print items before registration
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
            # Save to the CSV file with exact format
            with open(Person.path_to_person_data, "a") as f:
                f.write(", ".join(items_list) + "\n")
            if print_debug:
                print(f"Person registered with ID {new_id}")
        else:
            print("WARNING: Person NOT Registered!")
        return

    def _load_global_data(self, path_to_data_csv):
        print_debug = True
        print(f"------ _load_global_data() ------") if (print_debug == True) else False
        data_header, data_lines_len, data_lines = Functions_Csv.import_csv_cleaned(path_to_data_csv)
        print(f"- data_lines: {data_lines}") if (print_debug == True) else False
        id_header_index = data_header.index("id")
        print(f"- Data {path_to_data_csv} [{data_lines_len}]: {data_lines}") if (print_debug == True) else False
        return data_lines
        
    def _sort_datetimes_by_start_datetime(self, datetimes_list):
        print_debug = False
        print(f"------ _sort_datetimes() ------") if (print_debug == True) else False
        start_datetime_index = 1
        datetimes_list.sort(key=lambda d: d[1])
        
    def search_generically(self, search_str, role_key="", search_accuracy=0.7):
        """
        inputs:
            search_str: the string we are searching each attribute for (str).
        returns:
            matched: a list of persons who share the memory addresses* of self.persons, thus if they are changed, actual self.persons are changed as well.
        """
        print_debug = True
        print(f"------ search_generically() for '{search_str}' ------") if (print_debug == True) else False
        search_words = search_str.lower().split(" ")
        matched = []
        if (role_key):
            role_specific_persons = [x for x in self.persons if (role_key in x.role)]
        else:
            role_specific_persons = self.persons
        for person in role_specific_persons:
            # Get all string attributes
            person_values = [v.lower() for v in vars(person).values() if isinstance(v, str)]
            best_ratio = 0
            
            word_scores = []
            for word in search_words:
                best_word_ratio = 0
                for val in person_values:
                    ratio = difflib.SequenceMatcher(None, word, val).ratio()
                    if ratio > best_word_ratio:
                        best_word_ratio = ratio
                word_scores.append(best_word_ratio)

            # Aggregate score (average works well for multi-word searches)
            final_score = sum(word_scores) / len(word_scores)

            if final_score >= search_accuracy:
                matched.append((person, final_score))

            # Only keep persons above cutoff
            if best_ratio >= search_accuracy:
                matched.append((person, best_ratio))
        
        # Sort by best ratio descending
        matched.sort(key=lambda x: x[1], reverse=True)

        # Keep only person objects
        matched = [s for s, r in matched]
        matched_len = len(matched)
        
        print(f"Matched Persons [{matched_len}]: ")
        [print(f"- {x}") for x in matched]
        self.search_results = matched
        return matched

    def search_for_attr(self, search_attr, search_accuracy=0.9):
        print_debug = True
        print(f"------ search_for_attr() for '{search_attr}'------") if (print_debug == True) else False
        matches = difflib.get_close_matches(search_attr.lower(), self._person_attributes, n=1, cutoff=search_accuracy)
        if (not matches):
            print(f"Attribute '{search_attr}' not found!")
        else:
            matches = matches[0]
            print(f"Attribute '{search_attr}' found as '{matches}'")
        return matches

    def search_by_key(self, search_attr, search_str, role_key="", search_accuracy=0.9):
        """
        inputs:
            search_attr: the only attribute we want to consider when searching for search_str (str).
            search_str: the string we are searching each attribute for (str).
        returns:
            matched_persons: a list of persons who share the memory addresses* of self.persons, thus if they are changed, actual self.persons are changed as well.
        """
        print_debug = True
        print(f"------ search_by_key() for '{search_attr}' == '{search_str}' ------") if (print_debug == True) else False
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
                print(f"Matched Persons [{matched_len}]: ")
                [print(f"- {x}") for x in matched]
                self.search_results = matched
        return matched
    
    def print_global_commitments(self):
        print_debug = True
        print(f"------ print_global_commitments() ------") if (print_debug == True) else False
        print(f"Global Commitments [{len(self.commitments)}]: ")
        [print(f"- {x}") for x in self.commitments]
            
    def print_selected(self):
        print_debug = True
        print(f"------ print_selected() ------") if (print_debug == True) else False
        print(f"Selected [{len(self.selected)}]: ")
        [print(f"- {x}") for x in self.selected]
    def append_selected(self, person):
        print_debug = True
        print(f"------ append_selected() ------") if (print_debug == True) else False
        self.selected.append(person)
    def append_selected_intersection(self, intersection):
        print_debug = True
        print(f"------ append_selected_intersection() ------") if (print_debug == True) else False
        self.selected_intersections.append(intersection)
    
    def clear_working_memory(self):
        print_debug = True
        print(f"------ clear_working_memory() ------") if (print_debug == True) else False
        self.search_results = []
        self.selected = []
        self.selected_intersections = []
        
    def print_availability(self, person):
        print_debug = True
        print(f"------ print_availability() for '{person}' ------") if (print_debug == True) else False
        person.print_availability()
    def create_availability(self, person, start_datetime, end_datetime):
        print_debug = True
        print(f"------ create_availability() for '{person}' ------") if (print_debug == True) else False
        person.create_availability(start_datetime, end_datetime)
    def remove_availability(self, person, start_datetime, end_datetime):
        print_debug = True
        print(f"------ remove_availability() for '{person}' ------") if (print_debug == True) else False
        person.remove_availability(start_datetime, end_datetime)
    
    def get_intersecting_availability(self, target_persons=[]):
        print_debug = True
        FMT = "%Y-%m-%d %H:%M:%S%z"
        print(f"------ get_intersecting_availability() ------") if (print_debug == True) else False
        
        if (not target_persons):
            target_persons = self.selected
            
        target_persons_len = len(target_persons)
        availabilities = []
        for i, person in enumerate(target_persons):
            availability = person.availability
            availabilities.append(availability)
            print(f"Availability {i+1}/{target_persons_len} [{len(availability)}]: {availability}") if (print_debug == True) else False
        
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
                        this_intersections.append([
                            f"{cid}&{nid}",
                            start.isoformat(sep=" "),
                            end.isoformat(sep=" "),
                        ])

            # Move forward with the new this_intersections
            intersections = this_intersections

            # Early exit if nothing overlaps anymore
            if not intersections:
                break
        
        print(f"Availability Intersections [{len(intersections)}]: {intersections}") if (print_debug == True) else False
        self.selected_intersections = []
        return intersections
        
    def create_intersecting_commitments(self, remove_availability=False):
        print_debug = True
        FMT = "%Y-%m-%d %H:%M:%S%z"
        print(f"------ create_intersecting_commitments() ------") if (print_debug == True) else False
        
        # Create Global Commitments
        intersections_len = len(self.selected_intersections)
        for i, intersection in enumerate(self.selected_intersections):
            print(f"Intersection {i+1}/{intersections_len}: {intersection}") if (print_debug == True) else False
            a_line = f"{intersection[0]}, {intersection[1]}, {intersection[2]}\n"
            if (intersection not in self.commitments):
                # Append & Write
                self.commitments.append(intersection)
                with open(self.path_to_global_commitments_data, "a") as f:
                    f.write(a_line)
                print(f"- Global Datetime Created: {intersection}") if (print_debug == True) else False
            else:
                print(f"- Global Datetime Already Exists (Not Created): {intersection}") if (print_debug == True) else False
        self._sort_datetimes_by_start_datetime(self.commitments)
        
        # Create Person-Wise Commitments
        for i, intersection in enumerate(self.selected_intersections):
            print(f"Intersection {i+1}/{intersections_len}: {intersection}") if (print_debug == True) else False
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
                print(f"- Matching ID ({person.id} in {intersection_ids})?: {person.id in intersection_ids}") if (print_debug == True) else False
                
                availability = deepcopy(person.availability)
                commitments = deepcopy(person.commitments)
                
                person.create_commitment(datetime_start_utc, datetime_end_utc)
                
                if (remove_availability):
                    person.remove_availability(datetime_start_utc, datetime_end_utc)
                
                print(f"------ (return to) create_intersecting_commitments() ------") if (print_debug == True) else False
                print(f"- Availability (Before) {i+1}/{target_persons_len} [{len(availability)}]: {availability}") if (print_debug == True) else False
                print(f"- Commitments (Before) {i+1}/{target_persons_len} [{len(commitments)}]: {commitments}") if (print_debug == True) else False
                
                availability = person.availability
                commitments = person.commitments
                
                print(f"- Availability (After) {i+1}/{target_persons_len} [{len(availability)}]: {availability}") if (print_debug == True) else False
                print(f"- Commitments (After) {i+1}/{target_persons_len} [{len(commitments)}]: {commitments}") if (print_debug == True) else False
        
        self.print_global_commitments()
        return

    def convert_commitments_to_meetings(self):
        print_debug = True
        print(f"------ convert_commitments_to_meetings() ------") if (print_debug == True) else False
        # Gather evidence whether the meeting occurred; who attended, etc.
        
        # 
        return
    
class Person():
    path_to_person_data = "data\\person.csv" # Default 
    path_to_person_availability_data = "data\\person_availability.csv" # Default
    path_to_person_commitments_data = "data\\person_commitments.csv" # Default
    
    def __init__(self, items):
        self.role = items[0]
        self.first_name = items[1]
        self.last_name = items[2]
        self.id = items[3]
        self.family_id = items[4]
        self.date_registered = items[5]
        self.date_of_birth = items[6]
        self.address = items[7]
        self.phone_number = items[8]
        self.email = items[9]
        self.rate = items[10]
        self.balance = items[11]
        self.timezone = items[12]
        self.comments = items[13]
        
        # Load Data (e.g., Availability, Lessons History, Balance History)
        self.availability = self._load_data(self.path_to_person_availability_data)
        self.commitments = self._load_data(self.path_to_person_commitments_data)
        
    def __str__(self):
        string = f"Person: {self.role}, {self.first_name}, {self.last_name}, {self.id}, {self.family_id}, {self.date_registered}, {self.date_of_birth}, {self.address}, {self.phone_number}, {self.email}, {self.rate}, {self.balance}, {self.timezone}, {self.comments}"
        return string
        
    def __eq__(self, target):
        result = self.id == target.id
        return result
        
    def __lt__(self, target):
        if (self == target):
            result = False
        else:
            result = (self.first_name.lower(), self.last_name.lower(), self.id) < (target.first_name.lower(), self.last_name.lower(), self.id)
        return result
    
    def __le__(self, target):
        result = (self == target) or (self < target)
        
    def _print_self_basic(self):
        print(f"Person: {self.first_name}, {self.last_name}, {self.id}")
        
    def _load_data(self, path_to_data_csv):
        print_debug = True
        print(f"------ _load_data() ------") if (print_debug == True) else False
        data_header, data_lines_len, data_lines = Functions_Csv.import_csv_cleaned(path_to_data_csv)
        print(f"- data_lines: {data_lines}") if (print_debug == True) else False
        id_header_index = data_header.index("id")
        data_id_matched = [x for x in data_lines if (x[id_header_index].strip() == self.id.strip())]
        self._print_self_basic() if (print_debug == True) else False
        print(f"- Data {path_to_data_csv} [{len(data_id_matched)}]: {data_id_matched}") if (print_debug == True) else False
        return data_id_matched
        
    def _sort_datetimes(self, datetimes_list):
        print_debug = False
        print(f"------ _sort_datetimes() ------") if (print_debug == True) else False
        datetimes_list.sort()
        
    def _create_datetime(self, datetimes_list, path_to_datetimes_csv, start_datetime, end_datetime):
        print_debug = True
        print(f"------ _create_datetime() ------") if (print_debug == True) else False
        start_datetime_utc = start_datetime.astimezone(ZoneInfo("UTC"))
        end_datetime_utc = end_datetime.astimezone(ZoneInfo("UTC"))
        a_line = f"{self.id}, {start_datetime_utc}, {end_datetime_utc}\n"
        a_split = [x.strip() for x in a_line.split(",")]
        # Check Existing File & Correct Format
        with open(path_to_datetimes_csv, "r") as f:
            lines = f.readlines()
            lines_len = len(lines)
        if (lines_len == 0):
            print(f"ERROR: File ({path_to_datetimes_csv}) is Empty. Exiting.")
            exit()
        else:
            if ("\n" not in lines[-1]):
                a_line = "\n" + a_line
        # Append & Write Accordingly
        if (a_split not in datetimes_list):
            # Merge with existing overlapping datetimes (if any)
            datetime_to_remove = []
            for id_old, start_datetime_utc_old_str, end_datetime_utc_old_str in datetimes_list:
                start_datetime_utc_old = datetime.fromisoformat(start_datetime_utc_old_str)
                end_datetime_utc_old = datetime.fromisoformat(end_datetime_utc_old_str)
                if (start_datetime_utc <= start_datetime_utc_old) and (end_datetime_utc >= end_datetime_utc_old): # New is engulfing old
                    self._print_self_basic() if (print_debug == True) else False
                    print(f"- Datetimes Overlap (New Engulfs Old): {start_datetime_utc}->{end_datetime_utc} vs. {start_datetime_utc_old}->{end_datetime_utc_old}") if (print_debug == True) else False
                    # remove old start/end datetimes
                    datetime_to_remove.append([start_datetime_utc_old, end_datetime_utc_old])
                elif (start_datetime_utc_old <= start_datetime_utc <= end_datetime_utc_old) or (start_datetime_utc_old <= end_datetime_utc <= end_datetime_utc_old):
                    if (start_datetime_utc <= start_datetime_utc_old) and (end_datetime_utc <= end_datetime_utc_old): # New overlaps before old
                        self._print_self_basic() if (print_debug == True) else False
                        print(f"- Datetimes Overlap (New In/Before Old): {start_datetime_utc}->{end_datetime_utc} vs. {start_datetime_utc_old}->{end_datetime_utc_old}") if (print_debug == True) else False
                        end_datetime_utc = end_datetime_utc_old
                        # remove old start/end datetimes
                        datetime_to_remove.append([start_datetime_utc_old, end_datetime_utc_old])
                    elif (start_datetime_utc >= start_datetime_utc_old) and (end_datetime_utc >= end_datetime_utc_old): # New overlaps after old
                        self._print_self_basic() if (print_debug == True) else False
                        print(f"- Datetimes Overlap (New In/After Old): {start_datetime_utc}->{end_datetime_utc} vs. {start_datetime_utc_old}->{end_datetime_utc_old}") if (print_debug == True) else False
                        start_datetime_utc = start_datetime_utc_old
                        # remove old start/end datetimes
                        datetime_to_remove.append([start_datetime_utc_old, end_datetime_utc_old])
                    elif (start_datetime_utc >= start_datetime_utc_old) and (end_datetime_utc <= end_datetime_utc_old): # New is within old
                        self._print_self_basic() if (print_debug == True) else False
                        print(f"- Datetimes Overlap (New Within Old): {start_datetime_utc}->{end_datetime_utc} vs. {start_datetime_utc_old}->{end_datetime_utc_old}") if (print_debug == True) else False
                        start_datetime_utc = start_datetime_utc_old
                        end_datetime_utc = end_datetime_utc_old
            # Remove any datetime to remove
            for atr_start_time, atr_end_time in datetime_to_remove:
                self.remove_availability(atr_start_time, atr_end_time)
            # Use merged (if any) line and split
            a_line = f"{self.id}, {start_datetime_utc}, {end_datetime_utc}\n"
            a_split = [x.strip() for x in a_line.split(",")]
            if (a_split not in datetimes_list):
                # Append & Write
                datetimes_list.append(a_split)
                with open(path_to_datetimes_csv, "a") as f:
                    f.write(a_line)
                self._print_self_basic() if (print_debug == True) else False
                print(f"- Datetime Created: {a_split}") if (print_debug == True) else False
            else:
                self._print_self_basic() if (print_debug == True) else False
                print(f"- Datetime Already Exists (Not Created): {a_split}") if (print_debug == True) else False
        else:
            self._print_self_basic() if (print_debug == True) else False
            print(f"- Datetime Already Exists (Not Created): {a_split}") if (print_debug == True) else False
        self._sort_datetimes(datetimes_list)
        
    def _remove_datetime(self, datetimes_list, path_to_datetimes_csv, start_datetime, end_datetime):
        print_debug = True
        print(f"------ _remove_datetime() ------") if (print_debug == True) else False
        start_datetime_utc = start_datetime.astimezone(ZoneInfo("UTC"))
        end_datetime_utc = end_datetime.astimezone(ZoneInfo("UTC"))
        datetime_to_remove = []
        datetime_to_add = []
        for id_old, start_datetime_utc_old_str, end_datetime_utc_old_str in datetimes_list:
            start_datetime_utc_old = datetime.fromisoformat(start_datetime_utc_old_str)
            end_datetime_utc_old = datetime.fromisoformat(end_datetime_utc_old_str)
            if (start_datetime_utc == start_datetime_utc_old) and (end_datetime_utc == end_datetime_utc_old):
                datetime_to_remove.append([start_datetime_utc_old_str, end_datetime_utc_old_str])
                self._print_self_basic() if (print_debug == True) else False
                print(f"- Datetime Removing (Direct Match): {start_datetime_utc} -> {end_datetime_utc}") if (print_debug == True) else False
            elif (start_datetime_utc <= start_datetime_utc_old) and (end_datetime_utc >= end_datetime_utc_old): # New is engulfing old
                datetime_to_remove.append([start_datetime_utc_old_str, end_datetime_utc_old_str])
                self._print_self_basic() if (print_debug == True) else False
                print(f"- Datetime Removing (Engulfing Match): {start_datetime_utc_old} -> {end_datetime_utc_old}") if (print_debug == True) else False
            elif (start_datetime_utc_old <= start_datetime_utc <= end_datetime_utc_old) or (start_datetime_utc_old <= end_datetime_utc <= end_datetime_utc_old):
                if (start_datetime_utc <= start_datetime_utc_old) and (end_datetime_utc <= end_datetime_utc_old): # New overlaps before old
                    datetime_to_remove.append([start_datetime_utc_old_str, end_datetime_utc_old_str])
                    self._print_self_basic() if (print_debug == True) else False
                    print(f"- Datetime Removing (Removal In/Before Match): {start_datetime_utc}->{end_datetime_utc}") if (print_debug == True) else False
                    datetime_to_add.append([end_datetime_utc, end_datetime_utc_old])
                    print(f"- Datetime Re-Add (Split After Match): {end_datetime_utc}->{end_datetime_utc_old}") if (print_debug == True) else False
                elif (start_datetime_utc >= start_datetime_utc_old) and (end_datetime_utc >= end_datetime_utc_old): # New overlaps after old
                    datetime_to_remove.append([start_datetime_utc_old_str, end_datetime_utc_old_str])
                    self._print_self_basic() if (print_debug == True) else False
                    print(f"- Datetime Removing (Removal In/After Match): {start_datetime_utc}->{end_datetime_utc}") if (print_debug == True) else False
                    datetime_to_add.append([start_datetime_utc_old, start_datetime_utc])
                    print(f"- Datetime Re-Add (Split Before Match): {start_datetime_utc_old}->{start_datetime_utc}") if (print_debug == True) else False
                elif (start_datetime_utc >= start_datetime_utc_old) and (end_datetime_utc <= end_datetime_utc_old): # New is within old
                    datetime_to_remove.append([start_datetime_utc_old_str, end_datetime_utc_old_str])
                    self._print_self_basic() if (print_debug == True) else False
                    print(f"- Datetimes Removing (Removal In Match - Splitting): {start_datetime_utc}->{end_datetime_utc}") if (print_debug == True) else False
                    datetime_to_add.append([start_datetime_utc_old, start_datetime_utc])
                    print(f"- Datetime Re-Add (Split Before Match): {start_datetime_utc_old}->{start_datetime_utc}") if (print_debug == True) else False
                    datetime_to_add.append([end_datetime_utc, end_datetime_utc_old])
                    print(f"- Datetime Re-Add (Split After Match): {end_datetime_utc}->{end_datetime_utc_old}") if (print_debug == True) else False
        # Remove any availability to remove
        for atr_start_time_str, atr_end_time_str in datetime_to_remove:
            ltr = [self.id, atr_start_time_str, atr_end_time_str]
            # Remove from availability
            idx = datetimes_list.index(ltr)
            datetimes_list.pop(idx)
            with open(path_to_datetimes_csv, "r") as src, tempfile.NamedTemporaryFile("w", delete=False) as tmp:
                for line in src:
                    line_split = [x.strip() for x in line.split(",")]
                    # skip the line ONLY if all three fields match
                    if not (line_split == ltr):
                        tmp.write(line)
            os.replace(tmp.name, path_to_datetimes_csv)
        # Create any availability to create
        for ata_start_time, ata_end_time in datetime_to_add:
            self._create_datetime(datetimes_list, path_to_datetimes_csv, ata_start_time, ata_end_time)
        self._sort_datetimes(datetimes_list)
    
    ### Operation-Specific Functions (For End-User Use) ###
    def print_availability(self):
        print_debug = True
        print(f"------ print_availability() ------") if (print_debug == True) else False
        print(f"Availability [{len(self.availability)}]: ")
        [print(f"- {x}") for x in self.availability]
    def create_availability(self, start_datetime, end_datetime):
        """
        Create availability slot/line to self.availability and write it to .csv.
        - Duplicates are not created/written.
        - Overlaps are resolved (e.g., if new availability is added within/before/after/engulfing existing, they merge into one bigger availability slot/line).
        """
        print_debug = True
        print(f"------ create_availability() ------") if (print_debug == True) else False
        self._create_datetime(self.availability, self.path_to_person_availability_data, start_datetime, end_datetime)
    def remove_availability(self, start_datetime, end_datetime):
        """
        Remove availability slot/line to self.availability and write it to .csv.
        - Duplicates are not removed/written.
        - Overlaps are resolved (e.g., if availability is removed within/before/after/engulfing existing, the slots/lines are changed to accomodate the removal command).
        """
        print_debug = True
        print(f"------ remove_availability() ------") if (print_debug == True) else False
        self._remove_datetime(self.availability, self.path_to_person_availability_data, start_datetime, end_datetime)
        
    def print_commitments(self):
        print_debug = True
        print(f"------ print_commitments() ------") if (print_debug == True) else False
        self._print_self_basic()
        print(f"Commitments [{len(self.commitments)}]: ")
        [print(f"- {x}") for x in self.commitments]
    def create_commitment(self, start_datetime, end_datetime):
        """
        Create commitment slot/line to self.commitments and write it to .csv.
        - Duplicates are not created/written.
        - Overlaps are resolved (e.g., if new commitment is added within/before/after/engulfing existing, they merge into one bigger commitment slot/line).
        """
        print_debug = True
        print(f"------ create_commitment() ------") if (print_debug == True) else False
        self._create_datetime(self.commitments, self.path_to_person_commitments_data, start_datetime, end_datetime)
    def remove_commitment(self, start_datetime, end_datetime):
        """
        Remove commitment slot/line to self.commitments and write it to .csv.
        - Duplicates are not removed/written.
        - Overlaps are resolved (e.g., if commitment is removed within/before/after/engulfing existing, the slots/lines are changed to accomodate the removal command).
        """
        print_debug = True
        print(f"------ remove_commitment() ------") if (print_debug == True) else False
        self._remove_datetime(self.commitments, self.path_to_person_commitments_data, start_datetime, end_datetime)