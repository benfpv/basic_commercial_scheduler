import calendar
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


class Functions_Calendar_Ui_Admin:
    def __init__(self, current_datetime: datetime):
        if current_datetime.tzinfo is None:
            raise ValueError("current_datetime must be timezone-aware")
        self.current_datetime = current_datetime
        self.local_tz = current_datetime.tzinfo
        self.utc_tz = ZoneInfo("UTC")

    # --------------------- Helpers ---------------------
    def _safe_int(self, prompt: str, default: int | None = None) -> int | None:
        while True:
            inp = input(prompt).strip()
            if not inp and default is not None:
                return default
            try:
                return int(inp)
            except ValueError:
                print("❌ Please enter a number.")

    def _parse_time(self, time_str: str, date: datetime) -> datetime | None:
        """AM/PM by default (e.g. 3:30 PM), also accepts 24h (15:30)"""
        time_str = time_str.strip().upper().replace(".", ":")
        formats = ["%I:%M %p", "%I:%M%p", "%H:%M"]
        for fmt in formats:
            try:
                t = datetime.strptime(time_str, fmt)
                return date.replace(hour=t.hour, minute=t.minute)
            except ValueError:
                continue
        return None

    # --------------------- Timezone ---------------------
    def select_timezone(self):
        common = ["UTC", "America/Toronto", "America/New_York", "Europe/London",
                  "Europe/Paris", "Asia/Tokyo", "Australia/Sydney", "America/Los_Angeles"]
        print("---------- Common Timezones ----------")
        for i, tz in enumerate(common, 1):
            print(f"  {i:2}. {tz}")
        print("   0. Type custom timezone")
        choice = self._safe_int("Select (0 or number): ", default=0)
        if choice == 0:
            tz_str = input("Enter timezone (e.g. America/Toronto): ").strip()
        else:
            tz_str = common[choice - 1]
        try:
            self.local_tz = ZoneInfo(tz_str)
            print(f"✅ Timezone set to: {self.local_tz}")
        except Exception:
            print("❌ Invalid timezone — keeping current.")
            self.local_tz = self.current_datetime.tzinfo

    # --------------------- Calendar ---------------------
    def print_month(self, year: int, month: int):
        print(f"\n{calendar.month_name[month]} {year}")
        print(calendar.month(year, month).replace(
            str(self.current_datetime.day).rjust(2),
            f"[{self.current_datetime.day}]" if (year, month) == (self.current_datetime.year, self.current_datetime.month) else str(self.current_datetime.day).rjust(2)
        ))

    def select_date(self) -> datetime | None:
        year = self.current_datetime.year
        month = self.current_datetime.month
        while True:
            self.print_month(year, month)
            cmd = input("\nDay number or command (n=next month, p=prev month, nn=next year, pp=prev year, q=cancel): ").strip().lower()
            if cmd == 'q':
                return None
            if cmd == 'n':
                month += 1
            elif cmd == 'p':
                month -= 1
            elif cmd == 'nn':
                year += 1
            elif cmd == 'pp':
                year -= 1
            else:
                try:
                    day = int(cmd)
                    return datetime(year, month, day, tzinfo=self.local_tz)
                except (ValueError, TypeError):
                    print("❌ Invalid input.")
                    continue
            if month > 12:
                month = 1
                year += 1
            elif month < 1:
                month = 12
                year -= 1

    # --------------------- Time Range (AM/PM default) ---------------------
    def select_time_range(self, date: datetime) -> tuple[datetime, datetime] | None:
        while True:
            start_str = input(f"Start time for {date:%Y-%m-%d} (e.g. 3:30 PM): ").strip()
            start = self._parse_time(start_str, date)
            if start:
                break
            print("❌ Invalid time — try 3:30 PM or 15:30")

        while True:
            end_str = input("End time (e.g. 4:45 PM): ").strip()
            end = self._parse_time(end_str, date)
            if end and end > start:
                return start, end
            print("❌ End time must be after start.")

    # --------------------- Main function ---------------------
    def select_time_slot(self, current_datetime: datetime | None = None) -> list[tuple[datetime, datetime]]:
        if current_datetime:
            self.current_datetime = current_datetime
            self.local_tz = current_datetime.tzinfo

        print("---------- Time Slot Selector ----------")
        self.select_timezone()

        slots: list[tuple[datetime, datetime]] = []
        while True:
            print(f"---------- Slots [{len(slots)}] ----------")
            for i, (s, e) in enumerate(slots, 1):
                print(f"  {i}. {s:%Y-%m-%d %H:%M} → {e:%H:%M} (UTC)")
            print("---------- Actions: a = add  |  r = remove last  |  c = clear all  |  d = done ----------")
            action = input("> ").strip().lower()
            if action == 'd':
                break
            elif action == 'r' and slots:
                slots.pop()
                print("✅ Last slot removed.")
            elif action == 'c':
                slots.clear()
                print("✅ All slots cleared.")
            elif action == 'a':
                date = self.select_date()
                if not date:
                    continue
                times = self.select_time_range(date)
                if times:
                    start_utc = times[0].astimezone(self.utc_tz)
                    end_utc = times[1].astimezone(self.utc_tz)
                    slots.append((start_utc, end_utc))
                    print(f"✅ Added: {start_utc:%Y-%m-%d %H:%M} → {end_utc:%H:%M} (UTC)")
            else:
                print("❌ Unknown command.")

        if not slots:
            print("❌ No slots selected.")
            return []

        # ==================== CONFIRMATION ====================
        print(f"---------- Confirm Slots [{len(slots)}] ----------")
        for i, (s, e) in enumerate(slots, 1):
            print(f"  {i}. {s:%Y-%m-%d %H:%M} → {e:%H:%M} (UTC)")
        confirm = input("Confirm? (y/n): ").strip().lower()
        if confirm != 'y':
            return []

        # ==================== PROPAGATION ====================
        print("---------- Propagate Across Future Weeks ----------")
        print("  Enter additional weeks to repeat all slots (e.g. 3 = same slots for 3 more weeks).")
        print("  Press Enter / 0 to skip.")
        raw = input("  Weeks: ").strip()
        try:
            weeks = int(raw) if raw else 0
        except ValueError:
            weeks = 0

        if weeks > 0:
            base_slots = list(slots)
            for w in range(1, weeks + 1):
                delta = timedelta(weeks=w)
                for s, e in base_slots:
                    slots.append((s + delta, e + delta))
            print(f"✅ Propagated: {len(base_slots)} slot(s) × {weeks} week(s) = {len(slots)} total.")
            print(f"---------- All Slots [{len(slots)}] ----------")
            for i, (s, e) in enumerate(slots, 1):
                print(f"  {i}. {s:%Y-%m-%d %H:%M} → {e:%H:%M} (UTC)")

        return slots