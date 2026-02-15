

import os
import tempfile
import difflib
from datetime import datetime
from zoneinfo import ZoneInfo
from copy import deepcopy

from functions_csv import *

class Person():
    path_to_person_data = "data\\person.csv" # Default 
    path_to_person_availability_data = "data\\person_availability.csv" # Default
    path_to_person_commitments_data = "data\\person_commitments.csv" # Default
    path_to_person_meetings_data = "data\\person_meetings.csv" # Default
    
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
        
        self.print_debug = True
        
        ### Load Static (or LTM) Variables (e.g., Availability, Lessons History, Balance History)
        self.availability = self._load_data(self.path_to_person_availability_data)
        self.commitments = self._load_data(self.path_to_person_commitments_data)
        self.meetings = self._load_data(self.path_to_person_meetings_data)
        
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
        print(f"------ _load_data() ------") if (self.print_debug == True) else False
        data_header, data_lines_len, data_lines = Functions_Csv.import_csv_cleaned(path_to_data_csv)
        print(f"- data_lines: {data_lines}") if (self.print_debug == True) else False
        id_header_index = data_header.index("id")
        data_id_matched = [x for x in data_lines if (x[id_header_index].strip() == self.id.strip())]
        self._print_self_basic() if (self.print_debug == True) else False
        print(f"- Data {path_to_data_csv} [{len(data_id_matched)}]: {data_id_matched}") if (self.print_debug == True) else False
        return data_id_matched
        
    def _sort_datetimes(self, datetimes_list):
        print(f"------ _sort_datetimes() ------") if (self.print_debug == True) else False
        datetimes_list.sort()
        
    def _create_datetime(self, datetimes_list, path_to_datetimes_csv, start_datetime, end_datetime):
        print(f"------ _create_datetime() ------") if (self.print_debug == True) else False
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
                    self._print_self_basic() if (self.print_debug == True) else False
                    print(f"- Datetimes Overlap (New Engulfs Old): {start_datetime_utc}->{end_datetime_utc} vs. {start_datetime_utc_old}->{end_datetime_utc_old}") if (self.print_debug == True) else False
                    # remove old start/end datetimes
                    datetime_to_remove.append([start_datetime_utc_old, end_datetime_utc_old])
                elif (start_datetime_utc_old <= start_datetime_utc <= end_datetime_utc_old) or (start_datetime_utc_old <= end_datetime_utc <= end_datetime_utc_old):
                    if (start_datetime_utc <= start_datetime_utc_old) and (end_datetime_utc <= end_datetime_utc_old): # New overlaps before old
                        self._print_self_basic() if (self.print_debug == True) else False
                        print(f"- Datetimes Overlap (New In/Before Old): {start_datetime_utc}->{end_datetime_utc} vs. {start_datetime_utc_old}->{end_datetime_utc_old}") if (self.print_debug == True) else False
                        end_datetime_utc = end_datetime_utc_old
                        # remove old start/end datetimes
                        datetime_to_remove.append([start_datetime_utc_old, end_datetime_utc_old])
                    elif (start_datetime_utc >= start_datetime_utc_old) and (end_datetime_utc >= end_datetime_utc_old): # New overlaps after old
                        self._print_self_basic() if (self.print_debug == True) else False
                        print(f"- Datetimes Overlap (New In/After Old): {start_datetime_utc}->{end_datetime_utc} vs. {start_datetime_utc_old}->{end_datetime_utc_old}") if (self.print_debug == True) else False
                        start_datetime_utc = start_datetime_utc_old
                        # remove old start/end datetimes
                        datetime_to_remove.append([start_datetime_utc_old, end_datetime_utc_old])
                    elif (start_datetime_utc >= start_datetime_utc_old) and (end_datetime_utc <= end_datetime_utc_old): # New is within old
                        self._print_self_basic() if (self.print_debug == True) else False
                        print(f"- Datetimes Overlap (New Within Old): {start_datetime_utc}->{end_datetime_utc} vs. {start_datetime_utc_old}->{end_datetime_utc_old}") if (self.print_debug == True) else False
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
                self._print_self_basic() if (self.print_debug == True) else False
                print(f"- Datetime Created: {a_split}") if (self.print_debug == True) else False
            else:
                self._print_self_basic() if (self.print_debug == True) else False
                print(f"- Datetime Already Exists (Not Created): {a_split}") if (self.print_debug == True) else False
        else:
            self._print_self_basic() if (self.print_debug == True) else False
            print(f"- Datetime Already Exists (Not Created): {a_split}") if (self.print_debug == True) else False
        self._sort_datetimes(datetimes_list)
        
    def _remove_datetime(self, datetimes_list, path_to_datetimes_csv, start_datetime, end_datetime):
        print(f"------ _remove_datetime() ------") if (self.print_debug == True) else False
        start_datetime_utc = start_datetime.astimezone(ZoneInfo("UTC"))
        end_datetime_utc = end_datetime.astimezone(ZoneInfo("UTC"))
        datetime_to_remove = []
        datetime_to_add = []
        for id_old, start_datetime_utc_old_str, end_datetime_utc_old_str in datetimes_list:
            start_datetime_utc_old = datetime.fromisoformat(start_datetime_utc_old_str)
            end_datetime_utc_old = datetime.fromisoformat(end_datetime_utc_old_str)
            if (start_datetime_utc == start_datetime_utc_old) and (end_datetime_utc == end_datetime_utc_old):
                datetime_to_remove.append([start_datetime_utc_old_str, end_datetime_utc_old_str])
                self._print_self_basic() if (self.print_debug == True) else False
                print(f"- Datetime Removing (Direct Match): {start_datetime_utc} -> {end_datetime_utc}") if (self.print_debug == True) else False
            elif (start_datetime_utc <= start_datetime_utc_old) and (end_datetime_utc >= end_datetime_utc_old): # New is engulfing old
                datetime_to_remove.append([start_datetime_utc_old_str, end_datetime_utc_old_str])
                self._print_self_basic() if (self.print_debug == True) else False
                print(f"- Datetime Removing (Engulfing Match): {start_datetime_utc_old} -> {end_datetime_utc_old}") if (self.print_debug == True) else False
            elif (start_datetime_utc_old <= start_datetime_utc <= end_datetime_utc_old) or (start_datetime_utc_old <= end_datetime_utc <= end_datetime_utc_old):
                if (start_datetime_utc <= start_datetime_utc_old) and (end_datetime_utc <= end_datetime_utc_old): # New overlaps before old
                    datetime_to_remove.append([start_datetime_utc_old_str, end_datetime_utc_old_str])
                    self._print_self_basic() if (self.print_debug == True) else False
                    print(f"- Datetime Removing (Removal In/Before Match): {start_datetime_utc}->{end_datetime_utc}") if (self.print_debug == True) else False
                    datetime_to_add.append([end_datetime_utc, end_datetime_utc_old])
                    print(f"- Datetime Re-Add (Split After Match): {end_datetime_utc}->{end_datetime_utc_old}") if (self.print_debug == True) else False
                elif (start_datetime_utc >= start_datetime_utc_old) and (end_datetime_utc >= end_datetime_utc_old): # New overlaps after old
                    datetime_to_remove.append([start_datetime_utc_old_str, end_datetime_utc_old_str])
                    self._print_self_basic() if (self.print_debug == True) else False
                    print(f"- Datetime Removing (Removal In/After Match): {start_datetime_utc}->{end_datetime_utc}") if (self.print_debug == True) else False
                    datetime_to_add.append([start_datetime_utc_old, start_datetime_utc])
                    print(f"- Datetime Re-Add (Split Before Match): {start_datetime_utc_old}->{start_datetime_utc}") if (self.print_debug == True) else False
                elif (start_datetime_utc >= start_datetime_utc_old) and (end_datetime_utc <= end_datetime_utc_old): # New is within old
                    datetime_to_remove.append([start_datetime_utc_old_str, end_datetime_utc_old_str])
                    self._print_self_basic() if (self.print_debug == True) else False
                    print(f"- Datetimes Removing (Removal In Match - Splitting): {start_datetime_utc}->{end_datetime_utc}") if (self.print_debug == True) else False
                    datetime_to_add.append([start_datetime_utc_old, start_datetime_utc])
                    print(f"- Datetime Re-Add (Split Before Match): {start_datetime_utc_old}->{start_datetime_utc}") if (self.print_debug == True) else False
                    datetime_to_add.append([end_datetime_utc, end_datetime_utc_old])
                    print(f"- Datetime Re-Add (Split After Match): {end_datetime_utc}->{end_datetime_utc_old}") if (self.print_debug == True) else False
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
        print(f"------ print_availability() ------") if (self.print_debug == True) else False
        self._print_self_basic()
        print(f"Availability [{len(self.availability)}]: ")
        [print(f"- {x}") for x in self.availability]
    def create_availability(self, start_datetime, end_datetime):
        """
        Create availability slot/line to self.availability and write it to .csv.
        - Duplicates are not created/written.
        - Overlaps are resolved (e.g., if new availability is added within/before/after/engulfing existing, they merge into one bigger availability slot/line).
        """
        print(f"------ create_availability() ------") if (self.print_debug == True) else False
        self._create_datetime(self.availability, self.path_to_person_availability_data, start_datetime, end_datetime)
    def remove_availability(self, start_datetime, end_datetime):
        """
        Remove availability slot/line to self.availability and write it to .csv.
        - Duplicates are not removed/written.
        - Overlaps are resolved (e.g., if availability is removed within/before/after/engulfing existing, the slots/lines are changed to accomodate the removal command).
        """
        print(f"------ remove_availability() ------") if (self.print_debug == True) else False
        self._remove_datetime(self.availability, self.path_to_person_availability_data, start_datetime, end_datetime)
        
    def print_commitments(self):
        print(f"------ print_commitments() ------") if (self.print_debug == True) else False
        self._print_self_basic()
        print(f"Commitments [{len(self.commitments)}]: ")
        [print(f"- {x}") for x in self.commitments]
    def create_commitment(self, start_datetime, end_datetime):
        """
        Create commitment slot/line to self.commitments and write it to .csv.
        - Duplicates are not created/written.
        - Overlaps are resolved (e.g., if new commitment is added within/before/after/engulfing existing, they merge into one bigger commitment slot/line).
        """
        print(f"------ create_commitment() ------") if (self.print_debug == True) else False
        self._create_datetime(self.commitments, self.path_to_person_commitments_data, start_datetime, end_datetime)
    def remove_commitment(self, start_datetime, end_datetime):
        """
        Remove commitment slot/line to self.commitments and write it to .csv.
        - Duplicates are not removed/written.
        - Overlaps are resolved (e.g., if commitment is removed within/before/after/engulfing existing, the slots/lines are changed to accomodate the removal command).
        """
        print(f"------ remove_commitment() ------") if (self.print_debug == True) else False
        self._remove_datetime(self.commitments, self.path_to_person_commitments_data, start_datetime, end_datetime)
        
    def print_meetings(self):
        print(f"------ print_meetings() ------") if (self.print_debug == True) else False
        self._print_self_basic()
        print(f"Meetings [{len(self.meetings)}]: ")
        [print(f"- {x}") for x in self.meetings]
    def create_meeting(self, start_datetime, end_datetime):
        """
        Create meeting slot/line to self.meetings and write it to .csv.
        - Duplicates are not created/written.
        - Overlaps are resolved (e.g., if new meeting is added within/before/after/engulfing existing, they merge into one bigger meeting slot/line).
        """
        print(f"------ create_meeting() ------") if (self.print_debug == True) else False
        self._create_datetime(self.meetings, self.path_to_person_meetings_data, start_datetime, end_datetime)
    def remove_meeting(self, start_datetime, end_datetime):
        """
        Remove meeting slot/line from self.meetings and write it to .csv.
        - Duplicates are not removed/written.
        - Overlaps are resolved (e.g., if meeting is removed within/before/after/engulfing existing, the slots/lines are adjusted to accommodate the removal).
        """
        print(f"------ remove_meeting() ------") if (self.print_debug == True) else False
        self._remove_datetime(self.meetings, self.path_to_person_meetings_data, start_datetime, end_datetime)
