from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


class Functions_Calendar_Ui:
    # Vibe Coded
    def __init__(self, current_datetime):
        if current_datetime.tzinfo is None:
            raise ValueError("current_datetime must be timezone-aware")
        self.current_datetime = current_datetime
        self.local_tz = current_datetime.tzinfo
        self.utc_tz = ZoneInfo("UTC")

    # -------- Print calendar month --------
    def print_month(self, year, month):
        print(f"\n      {datetime(year, month, 1):%B %Y}")
        print("Mo Tu We Th Fr Sa Su")

        first_day = datetime(year, month, 1)
        start_weekday = first_day.weekday()  # Monday=0

        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)

        num_days = (next_month - first_day).days

        print("   " * start_weekday, end="")

        for day in range(1, num_days + 1):
            print(f"{day:2}", end=" ")
            if (start_weekday + day) % 7 == 0:
                print()
        print("\n")

    # -------- Select a single time slot --------
    def select_single_slot(self, year, month):
        # Select date
        while True:
            self.print_month(year, month)
            day_input = input("Enter day number (or 'q' to cancel): ")

            if day_input.lower() == "q":
                return None

            if not day_input.isdigit():
                print("Invalid input.")
                continue

            day = int(day_input)

            try:
                selected_date = datetime(year, month, day, tzinfo=self.local_tz)
            except ValueError:
                print("Invalid date.")
                continue

            break

        # Select start time
        while True:
            time_input = input("Enter start time (HH:MM, 24h): ")

            try:
                hour, minute = map(int, time_input.split(":"))
                datetime_start_local = selected_date.replace(hour=hour, minute=minute)
                break
            except:
                print("Invalid time format.")

        # Select duration
        while True:
            duration_input = input("Enter duration (minutes): ")
            if not duration_input.isdigit():
                print("Invalid duration.")
                continue
            duration = int(duration_input)
            datetime_end_local = datetime_start_local + timedelta(minutes=duration)
            break

        # Convert to UTC
        datetime_start_utc = datetime_start_local.astimezone(self.utc_tz)
        datetime_end_utc = datetime_end_local.astimezone(self.utc_tz)

        return [datetime_start_utc, datetime_end_utc]

    # -------- Main callable function --------
    def select_time_slot(self, current_datetime=None):
        """
        Main method to select multiple slots.
        Returns a list of [start_utc, end_utc] pairs.
        """
        if current_datetime:
            # Override instance datetime if provided
            if current_datetime.tzinfo is None:
                raise ValueError("current_datetime must be timezone-aware")
            self.current_datetime = current_datetime
            self.local_tz = current_datetime.tzinfo

        year = self.current_datetime.year
        month = self.current_datetime.month
        slots = []

        print("\nSelect multiple time slots. Type 'done' when finished.\n")

        while True:
            user_choice = input("Add a new slot? (y/done): ").lower()
            if user_choice == "done":
                break
            elif user_choice != "y":
                print("Type 'y' to add or 'done' to finish.")
                continue

            slot = self.select_single_slot(year, month)
            if slot:
                slots.append(slot)
                print(f"Slot added: {slot[0]} to {slot[1]} (UTC)\n")

        if not slots:
            print("No slots selected.")
            return []

        # Confirmation
        print("\nYou selected the following slots:")
        for i, (start, end) in enumerate(slots, 1):
            print(f"{i}. {start} to {end} (UTC)")

        while True:
            confirm = input("Confirm? (y/n): ").lower()
            if confirm == "y":
                return slots
            elif confirm == "n":
                print("Selection cancelled.")
                return []
            else:
                print("Type 'y' to confirm or 'n' to cancel.")
