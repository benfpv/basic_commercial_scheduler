from datetime import datetime
from zoneinfo import ZoneInfo

class Functions_User_Register_Ui():
    def register_user():
        print("=== Register New User ===")
        print("Tip: Type 'cancel' at any prompt to cancel and go back.\n")

        # --- Strict dash-only date parser returning naive datetime ---
        def parse_date(s):
            s = s.strip()
            try:
                d = datetime.strptime(s, "%Y-%m-%d")
                return d  # naive datetime
            except:
                return None

        # --- Format phone number to +1 XXX-XXX-XXXX ---
        def format_phone(p):
            digits = "".join(c for c in p if c.isdigit())
            if len(digits) == 10:
                return f"+1 {digits[:3]}-{digits[3:6]}-{digits[6:]}"
            elif len(digits) == 11 and digits[0] == "1":
                return f"+1 {digits[1:4]}-{digits[4:7]}-{digits[7:]}"
            elif digits.startswith("1") and len(digits) > 11:
                return f"+1 {digits[1:4]}-{digits[4:7]}-{digits[7:11]}"
            else:
                return p  # fallback: return as is

        # --- Function to handle cancel check ---
        def get_input(prompt):
            user_input = input(prompt).strip()
            if user_input.lower() == 'cancel':
                print("Registration cancelled.")
                return None
            return user_input

        # --- Collect role, names, IDs ---
        while True:
            role = get_input("Role (type 'cancel' to cancel): ")
            if role is None: return None  # Cancel registration if 'cancel' is entered
            if role: break
            print("Role is required.")

        while True:
            first_name = get_input("First Name (type 'cancel' to cancel): ")
            if first_name is None: return None
            if first_name: break
            print("First Name is required.")
            
        while True:
            last_name = get_input("Last Name (type 'cancel' to cancel): ")
            if last_name is None: return None
            if last_name: break
            print("Last Name is required.")
            
        id = ""  # will be assigned later
        family_id = get_input("Family ID (if applicable) (type 'cancel' to cancel): ")
        if family_id is None: return None

        # --- Timezone selection ---
        example_timezones = ["UTC", "America/Toronto", "America/New_York", "Europe/London", "Asia/Tokyo", "Australia/Sydney"]
        print("Enter your timezone (IANA format). Examples:", ", ".join(example_timezones))
        while True:
            tz_input = get_input("Timezone (e.g., Europe/London) (type 'cancel' to cancel): ")
            if tz_input is None: return None
            try:
                tz = ZoneInfo(tz_input)
                timezone = tz.key  # canonical name
                break
            except:
                print("Invalid timezone. Enter a valid IANA timezone like 'Europe/London', 'America/New_York', etc.")

        # --- Date Registered (naive, default today) ---
        while True:
            date_registered_input = get_input("Date Registered (YYYY-MM-DD) [Leave blank for today] (type 'cancel' to cancel): ")
            if date_registered_input is None: return None
            if not date_registered_input:
                date_registered = datetime.today().date().isoformat()
                print(f"Date Registered set to today: {date_registered}")
                break
            dt_naive = parse_date(date_registered_input)
            if not dt_naive:
                print("Invalid date format. Try YYYY-MM-DD.")
                continue
            if dt_naive.date() > datetime.today().date():
                print("Date Registered cannot be in the future.")
            else:
                date_registered = dt_naive.date().isoformat()
                break

        # --- Date of Birth (naive) ---
        while True:
            date_of_birth_input = get_input("Date of Birth (YYYY-MM-DD) (type 'cancel' to cancel): ")
            if date_of_birth_input is None: return None
            dt_naive = parse_date(date_of_birth_input)
            if not dt_naive:
                print("Invalid date format. Try YYYY-MM-DD.")
                continue
            if dt_naive.date() >= datetime.today().date():
                print("Date of Birth must be in the past.")
            else:
                date_of_birth = dt_naive.date().isoformat()
                break

        # --- Address ---
        while True:
            address = get_input("Address (type 'cancel' to cancel): ")
            if address is None: return None
            if address: break
            print("Address is required.")

        # --- Phone Number ---
        while True:
            phone_input = get_input("Phone Number (digits, optional + for country code) (type 'cancel' to cancel): ")
            if phone_input is None: return None
            if not phone_input:
                phone_number = ""
                break
            phone_number = format_phone(phone_input)
            digits_only = "".join(c for c in phone_number if c.isdigit())
            if len(digits_only) < 10:
                print("Phone Number seems too short.")
            else:
                break

        # --- Email ---
        while True:
            email = get_input("Email (type 'cancel' to cancel): ")
            if email is None: return None
            if not email:
                print("Email is required.")
            elif "@" not in email or "." not in email:
                print("Invalid email format.")
            else:
                break

        # --- Rate ---
        while True:
            rate_input = get_input("Rate (type 'cancel' to cancel): ").strip().replace(",", "")
            if rate_input is None: return None
            try:
                r = float(rate_input)
                if r < 0: 
                    print("Rate cannot be negative.")
                else: 
                    rate = str(r); break
            except:
                print("Rate must be a number.")

        # --- Balance (optional) ---
        while True:
            balance_input = get_input("Balance (optional, type 'cancel' to cancel): ").strip().replace(",", "")
            if balance_input is None: return None
            if not balance_input:
                balance = ""
                break
            try:
                b = float(balance_input)
                balance = str(b)
                break
            except:
                print("Balance must be a number or left blank.")

        # --- Comments (optional) ---
        comments = get_input("Comments (optional, type 'cancel' to cancel): ")
        if comments is None: return None

        # --- Confirm ---
        print("\n=== Confirm User Information ===")
        print("Role:", role)
        print("First Name:", first_name)
        print("Last Name:", last_name)
        print("ID: <Will Be Auto-Generated if Empty>", id)
        print("Family ID: <Will Be Auto-Generated if Empty>", family_id)
        print("Date Registered:", date_registered)
        print("Date of Birth:", date_of_birth)
        print("Address:", address)
        print("Phone Number:", phone_number)
        print("Email:", email)
        print("Rate:", rate)
        print("Balance:", balance if balance else "0")
        print("Timezone:", timezone)
        print("Comments:", comments if comments else "")

        confirm = get_input("\nIs this information correct? (y/n): ").strip().lower()
        if confirm == "y":
            # Convert all items to strings
            items = {k: str(v).strip() if v is not None else "" for k, v in {
                "role": role,
                "first_name": first_name,
                "last_name": last_name,
                "id": id,
                "family_id": family_id,
                "date_registered": date_registered,
                "date_of_birth": date_of_birth,
                "address": address,
                "phone_number": phone_number,
                "email": email,
                "rate": rate,
                "balance": balance,
                "timezone": timezone,
                "comments": comments
            }.items()}
            print("Registering User.")
            return items
        else:
            print("Registration cancelled.")
            return None
