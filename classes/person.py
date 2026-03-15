

from datetime import datetime
from zoneinfo import ZoneInfo

from db import database

class Person():
    print_debug = False
    
    def __init__(self, items):
        ### Per-Person Profile ###
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
        
        ### Per-Person Scheduling & Financial History (loaded from DB) ###
        _availability_rows = database.fetch_all(
            "SELECT user_id, start_utc, end_utc FROM user_availabilities WHERE user_id=? ORDER BY start_utc",
            (int(self.id),)
        )
        self.availability = [[str(r["user_id"]), r["start_utc"], r["end_utc"]] for r in _availability_rows]

        _commitment_rows = database.fetch_all(
            """SELECT cp.user_id, c.start_utc, c.end_utc
               FROM commitment_participants cp
               JOIN commitments c ON cp.commitment_id = c.commitment_id
               WHERE cp.user_id = ?
               ORDER BY c.start_utc""",
            (int(self.id),)
        )
        self.commitments = [[str(r["user_id"]), r["start_utc"], r["end_utc"]] for r in _commitment_rows]

        _meetings_history_rows = database.fetch_all(
            """SELECT mp.user_id, m.start_utc, m.end_utc
               FROM meeting_participants mp
               JOIN meetings m ON mp.meeting_id = m.meeting_id
               WHERE mp.user_id = ?
               ORDER BY m.start_utc""",
            (int(self.id),)
        )
        self.meetings_history = [[str(r["user_id"]), r["start_utc"], r["end_utc"]] for r in _meetings_history_rows]

        _balance_rows = database.fetch_all(
            """SELECT user_id, associate_ids, start_utc, end_utc, amount, balance_after
               FROM balance_history WHERE user_id = ? ORDER BY entry_id""",
            (int(self.id),)
        )
        self.balance_history = [
            [str(r["user_id"]), r["associate_ids"] or "", r["start_utc"], r["end_utc"],
             str(r["amount"]), str(r["balance_after"])]
            for r in _balance_rows
        ]
        
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
        
    def _update_person_data(self):
        print("------ _update_person_data() ------") if self.print_debug else None
        database.execute(
            """UPDATE users SET role=?, first_name=?, last_name=?, family_id=?,
               date_registered=?, date_of_birth=?, address=?, phone_number=?,
               email=?, rate=?, balance=?, timezone=?, comments=?
               WHERE id=?""",
            (self.role, self.first_name, self.last_name, self.family_id,
             self.date_registered, self.date_of_birth, self.address,
             self.phone_number, self.email, float(self.rate), float(self.balance),
             self.timezone, self.comments, int(self.id))
        )
        
    def _sort_datetimes(self, datetimes_list):
        print(f"------ _sort_datetimes() ------") if (self.print_debug == True) else False
        datetimes_list.sort()
        
    def _create_datetime(self, datetimes_list, start_datetime, end_datetime):
        print(f"------ _create_datetime() ------") if (self.print_debug == True) else False
        start_datetime_utc = start_datetime.astimezone(ZoneInfo("UTC"))
        end_datetime_utc = end_datetime.astimezone(ZoneInfo("UTC"))
        a_line = f"{self.id}, {start_datetime_utc}, {end_datetime_utc}\n"
        a_split = [x.strip() for x in a_line.split(",")]
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
                self._remove_datetime(datetimes_list, atr_start_time, atr_end_time)
            # Use merged (if any) line and split
            a_line = f"{self.id}, {start_datetime_utc}, {end_datetime_utc}\n"
            a_split = [x.strip() for x in a_line.split(",")]
            if (a_split not in datetimes_list):
                datetimes_list.append(a_split)
                self._print_self_basic() if (self.print_debug == True) else False
                print(f"- Datetime Created: {a_split}") if (self.print_debug == True) else False
            else:
                self._print_self_basic() if (self.print_debug == True) else False
                print(f"- Datetime Already Exists (Not Created): {a_split}") if (self.print_debug == True) else False
        else:
            self._print_self_basic() if (self.print_debug == True) else False
            print(f"- Datetime Already Exists (Not Created): {a_split}") if (self.print_debug == True) else False
        self._sort_datetimes(datetimes_list)
        
    def _remove_datetime(self, datetimes_list, start_datetime, end_datetime):
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
        # Remove from in-memory list
        for atr_start_time_str, atr_end_time_str in datetime_to_remove:
            ltr = [self.id, atr_start_time_str, atr_end_time_str]
            if ltr in datetimes_list:
                datetimes_list.remove(ltr)
        # Re-add split segments
        for ata_start_time, ata_end_time in datetime_to_add:
            self._create_datetime(datetimes_list, ata_start_time, ata_end_time)
        self._sort_datetimes(datetimes_list)
    
    ### Operation-Specific Functions (For End-User Use) ###
    def print_availability(self):
        FMT = "%Y-%m-%d %H:%M:%S%z"
        print(f"------ print_availability() ------") if (self.print_debug == True) else False
        self._print_self_basic()
        print(f"Availability [{len(self.availability)}] (Timezone: {self.timezone}): ")
        if self.availability:
            for x in self.availability:
                start_datetime = datetime.strptime(x[1], FMT).astimezone(self.timezone)
                end_datetime = datetime.strptime(x[2], FMT).astimezone(self.timezone)
                print(f"- {start_datetime} -> {end_datetime}")
        else:
            print("- (none)")
    def create_availability(self, start_datetime, end_datetime):
        """
        Create availability slot for this person in memory and DB.
        - Duplicates are not created.
        - Overlaps are resolved (new slot merges with any overlapping existing slots).
        """
        print(f"------ create_availability() ------") if (self.print_debug == True) else False
        self._create_datetime(self.availability, start_datetime, end_datetime)
        self._sync_availability_to_db()
    def _sync_availability_to_db(self):
        """Dual-write: replaces all DB availability rows for this user with current in-memory state."""
        database.execute("DELETE FROM user_availabilities WHERE user_id=?", (int(self.id),))
        for row in self.availability:
            database.execute(
                "INSERT INTO user_availabilities (user_id, start_utc, end_utc) VALUES (?,?,?)",
                (int(self.id), row[1], row[2])
            )
    def remove_availability(self, start_datetime="", end_datetime="", target_index=None):
        """
        Remove availability slot for this person from memory and DB.
        - Overlaps are resolved (partial removals split existing slots accordingly).
        """
        print(f"------ remove_availability() ------") if (self.print_debug == True) else False
        if (target_index is not None):
            FMT = "%Y-%m-%d %H:%M:%S%z"
            this_datetimes = self.availability[target_index]
            start_datetime = datetime.strptime(this_datetimes[1], FMT)
            end_datetime = datetime.strptime(this_datetimes[2], FMT)
        self._remove_datetime(self.availability, start_datetime, end_datetime)
        self._sync_availability_to_db()
        
    def print_commitments(self):
        FMT = "%Y-%m-%d %H:%M:%S%z"
        print(f"------ print_commitments() ------") if (self.print_debug == True) else False
        self._print_self_basic()
        print(f"Commitments [{len(self.commitments)}] (Timezone: {self.timezone}): ")
        if self.commitments:
            for x in self.commitments:
                start_datetime = datetime.strptime(x[1], FMT).astimezone(self.timezone)
                end_datetime = datetime.strptime(x[2], FMT).astimezone(self.timezone)
                print(f"- {start_datetime} -> {end_datetime}")
        else:
            print("- (none)")
    def create_commitment(self, start_datetime, end_datetime):
        """
        Create commitment slot for this person in memory and DB.
        - Duplicates are not created.
        - Overlaps are resolved (new slot merges with any overlapping existing slots).
        """
        print(f"------ create_commitment() ------") if (self.print_debug == True) else False
        self._create_datetime(self.commitments, start_datetime, end_datetime)
        self._sync_commitment_to_db()
    def _sync_commitment_to_db(self):
        """Dual-write: syncs commitment_participants rows for this user with current in-memory state."""
        database.execute("DELETE FROM commitment_participants WHERE user_id=?", (int(self.id),))
        for row in self.commitments:
            c_row = database.fetch_one(
                "SELECT commitment_id FROM commitments WHERE start_utc=? AND end_utc=?",
                (row[1], row[2])
            )
            if c_row:
                database.execute(
                    "INSERT OR IGNORE INTO commitment_participants (commitment_id, user_id) VALUES (?,?)",
                    (c_row["commitment_id"], int(self.id))
                )
    def remove_commitment(self, start_datetime="", end_datetime="", target_index=None):
        """
        Remove commitment slot for this person from memory and DB.
        - Overlaps are resolved (partial removals split existing slots accordingly).
        """
        print(f"------ remove_commitment() ------") if (self.print_debug == True) else False
        if (target_index is not None):
            FMT = "%Y-%m-%d %H:%M:%S%z"
            this_datetimes = self.commitments[target_index]
            start_datetime = datetime.strptime(this_datetimes[1], FMT)
            end_datetime = datetime.strptime(this_datetimes[2], FMT)
        self._remove_datetime(self.commitments, start_datetime, end_datetime)
        self._sync_commitment_to_db()
        
    def print_meetings_history(self):
        FMT = "%Y-%m-%d %H:%M:%S%z"
        print(f"------ print_meetings_history() ------") if (self.print_debug == True) else False
        self._print_self_basic()
        print(f"Meetings History [{len(self.meetings_history)}] (Timezone: {self.timezone}): ")
        if self.meetings_history:
            for x in self.meetings_history:
                start_datetime = datetime.strptime(x[1], FMT).astimezone(self.timezone)
                end_datetime = datetime.strptime(x[2], FMT).astimezone(self.timezone)
                print(f"- {start_datetime} -> {end_datetime}")
        else:
            print("- (none)")
    def create_meeting(self, start_datetime, end_datetime):
        """
        Create meeting slot for this person in memory and DB.
        - Duplicates are not created.
        - Overlaps are resolved (new slot merges with any overlapping existing slots).
        """
        print(f"------ create_meeting() ------") if (self.print_debug == True) else False
        self._create_datetime(self.meetings_history, start_datetime, end_datetime)
        self._sync_meeting_to_db()
    def _sync_meeting_to_db(self):
        """Dual-write: syncs meeting_participants rows for this user with current in-memory state."""
        database.execute("DELETE FROM meeting_participants WHERE user_id=?", (int(self.id),))
        for row in self.meetings_history:
            m_row = database.fetch_one(
                "SELECT meeting_id FROM meetings WHERE start_utc=? AND end_utc=?",
                (row[1], row[2])
            )
            if m_row:
                database.execute(
                    "INSERT OR IGNORE INTO meeting_participants (meeting_id, user_id, attended) VALUES (?,?,1)",
                    (m_row["meeting_id"], int(self.id))
                )
    def remove_meeting(self, start_datetime="", end_datetime="", target_index=None):
        """
        Remove meeting slot for this person from memory and DB.
        - Overlaps are resolved (partial removals split existing slots accordingly).
        """
        print(f"------ remove_meeting() ------") if (self.print_debug == True) else False
        if (target_index is not None):
            FMT = "%Y-%m-%d %H:%M:%S%z"
            this_datetimes = self.meetings_history[target_index]
            start_datetime = datetime.strptime(this_datetimes[1], FMT)
            end_datetime = datetime.strptime(this_datetimes[2], FMT)
        self._remove_datetime(self.meetings_history, start_datetime, end_datetime)
        self._sync_meeting_to_db()

    def print_balance_history(self):
        print(f"------ print_balance_history() ------") if (self.print_debug == True) else False
        self._print_self_basic()
        print(f"Balance: {self.balance}")
        print(f"Balance History [{len(self.balance_history)}]: ")
        if self.balance_history:
            [print(f"- {x}") for x in self.balance_history]
        else:
            print("- (none)")

    def create_balance_entry(self, associate_ids_str, start_time_utc, end_time_utc, entry):
        print(f"------ create_balance_entry() ------") if (self.print_debug == True) else False
        # Calculate Balance
        self.balance = float(self.balance) + float(entry)
        self._update_person_data()
        # Build entry
        a_line = f"{self.id}, {associate_ids_str}, {start_time_utc}, {end_time_utc}, {entry}, {self.balance}\n"
        a_split = [x.strip() for x in a_line.split(",")]
        datetimes_only_split = a_split[0:5]  # exclude balance total to avoid duplicate entries
        balance_history_datetimes_only = [x[0:5] for x in self.balance_history]
        if (datetimes_only_split not in balance_history_datetimes_only):
            self.balance_history.append(a_split)
            database.execute(
                """INSERT INTO balance_history
                   (user_id, associate_ids, start_utc, end_utc, amount, balance_after)
                   VALUES (?,?,?,?,?,?)""",
                (int(self.id), associate_ids_str, str(start_time_utc), str(end_time_utc),
                 float(entry), float(self.balance))
            )
        self.print_balance_history() if (self.print_debug == True) else False