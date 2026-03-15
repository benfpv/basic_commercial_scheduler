from datetime import datetime
from zoneinfo import ZoneInfo


class Functions_Plan_Meeting_Ui_Admin:
    """
    Sub-UI for the plan_meeting flow.
    Shows available intersection windows for the selected persons, lets the admin
    pick a window and optionally trim the start/end time within its bounds, then
    returns the finalised list of [ids_str, start_utc_str, end_utc_str] items
    ready to be committed as intersecting commitments.
    """
    FMT = "%Y-%m-%d %H:%M:%S%z"

    def __init__(self, persons, intersections: list):
        self.persons = persons
        self.intersections = intersections  # list of [ids_str, start_utc_str, end_utc_str]
        self.local_tz = persons.current_timezone
        self.utc_tz = ZoneInfo("UTC")

    # ----- Helpers -----

    def _parse_time(self, time_str: str, anchor_date: datetime) -> datetime | None:
        """Parse HH:MM AM/PM or 24h time, anchored to the given date."""
        time_str = time_str.strip().upper().replace(".", ":")
        for fmt in ["%I:%M %p", "%I:%M%p", "%H:%M"]:
            try:
                t = datetime.strptime(time_str, fmt)
                return anchor_date.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
            except ValueError:
                continue
        return None

    def _fmt_local(self, utc_str: str) -> str:
        dt = datetime.strptime(utc_str, self.FMT).astimezone(self.local_tz)
        return dt.strftime("%Y-%m-%d %H:%M %Z")

    def _print_separator(self, label=""):
        print(f"---------- {label} ----------" if label else "----------------------------------------")

    def _print_intersection(self, idx: int, item: list):
        ids_str, start_str, end_str = item[0], item[1], item[2]
        start_local = datetime.strptime(start_str, self.FMT).astimezone(self.local_tz)
        end_local   = datetime.strptime(end_str,   self.FMT).astimezone(self.local_tz)
        duration_min = int((end_local - start_local).total_seconds() // 60)
        print(f"  [{idx}]  IDs: {ids_str}  |  {start_local:%Y-%m-%d %H:%M %Z} --> {end_local:%H:%M %Z}  ({duration_min} min)")

    # ----- Main entry point -----

    def run(self) -> list:
        """
        Interactive loop. Returns a (possibly empty) list of trimmed
        [ids_str, start_utc_str, end_utc_str] items to commit, or [] on cancel.
        """
        planned = []

        while True:
            print("")
            self._print_separator("Available Intersection Windows")
            if self.intersections:
                for i, item in enumerate(self.intersections):
                    self._print_intersection(i, item)
            else:
                print("  (none)")

            if planned:
                self._print_separator(f"Planned Commitments [{len(planned)}]")
                for i, item in enumerate(planned):
                    self._print_intersection(i, item)

            print("")
            print("  [index]  select window    |  d = done & commit    |  q = cancel all")
            cmd = input("  > ").strip().lower()

            if cmd == "q":
                print("Cancelled — no commitments created.")
                return []

            if cmd == "d":
                if not planned:
                    print("Nothing planned yet — select at least one window first.")
                    continue
                break

            if not cmd.isnumeric():
                print("Invalid input.")
                continue
            idx = int(cmd)
            if not (0 <= idx < len(self.intersections)):
                print(f"Index {idx} out of range.")
                continue

            item = self.intersections[idx]
            ids_str      = item[0]
            window_start = datetime.strptime(item[1], self.FMT).astimezone(self.local_tz)
            window_end   = datetime.strptime(item[2], self.FMT).astimezone(self.local_tz)
            duration_min = int((window_end - window_start).total_seconds() // 60)

            print("")
            self._print_separator(f"Window — IDs: {ids_str}")
            print(f"  Full window : {window_start:%Y-%m-%d %H:%M %Z}  -->  {window_end:%H:%M %Z}  ({duration_min} min)")
            print("")
            print("  f = use full window    |  t = trim start/end    |  q = back")
            choice = input("  > ").strip().lower()

            if choice == "q":
                continue

            elif choice == "f":
                planned.append(list(item))
                print(f"  Added full window.")

            elif choice == "t":
                # --- Trim start ---
                while True:
                    raw = input(f"  Start time (between {window_start:%H:%M} and {window_end:%H:%M}, e.g. 3:30 PM or 15:30): ").strip()
                    t_start = self._parse_time(raw, window_start)
                    if t_start and window_start <= t_start < window_end:
                        break
                    print(f"  Must be within {window_start:%H:%M} – {window_end:%H:%M}.")
                # --- Trim end ---
                while True:
                    raw = input(f"  End time   (between {t_start:%H:%M} and {window_end:%H:%M}): ").strip()
                    t_end = self._parse_time(raw, window_start)
                    if t_end and t_start < t_end <= window_end:
                        break
                    print(f"  Must be after {t_start:%H:%M} and no later than {window_end:%H:%M}.")
                t_start_utc = t_start.astimezone(self.utc_tz)
                t_end_utc   = t_end.astimezone(self.utc_tz)
                planned.append([
                    ids_str,
                    t_start_utc.strftime(self.FMT),
                    t_end_utc.strftime(self.FMT)
                ])
                trimmed_min = int((t_end - t_start).total_seconds() // 60)
                print(f"  Added: {t_start:%H:%M %Z} --> {t_end:%H:%M %Z}  ({trimmed_min} min)")

            else:
                print("Invalid choice.")

        return planned
