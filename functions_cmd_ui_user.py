
import os
from functions_calendar_ui import *
from functions_user_register_ui import *

class Functions_Cmd_Ui(): # DEMO ONLY - this is <ideal design
    def __init__(self, persons, print_debug=False, clear_console=True):
        self.persons = persons
        self.persons.print_debug = print_debug
        self.clear_console = clear_console

        self.current = "mainmenu"
        self.mainmenu = ["global_print_menu", "register_person", "search", "search_by_key", "selected_print_menu", "selected_availability_menu", "selected_commitments_menu", "selected_meetings_menu", "find_intersection", "clear_selections", "toggle_debug_outputs", "exit"]
        self.global_print_menu = ["print_global_active_meetings", "print_global_commitments", "print_global_meetings"]
        self.selected_print_menu = ["print_availability", "print_commitments", "print_meetings", "print_balance_history"]
        self.selected_availability_menu = ["print_availability", "create_availability", "remove_availability"]
        self.selected_commitments_menu = ["print_commitments", "create_commitments", "remove_commitments"]
        self.selected_meetings_menu = ["print_meetings", "create_meetings", "remove_meetings"]
        self.menu_loop()
        
    def menu_loop(self):
        exit_now = False
        while (not exit_now):
            self.persons.update()
            exit_now = self.print_current()
    
    def print_current_datetime(self):
        print(f"Current Datetime (as of): {self.persons.current_datetime}")
    def print_page_title(self, title):
        if (self.clear_console):
            os.system("cls") if (os.name == "nt") else os.system("clear")
        print(f"==================== HEADER ====================")
        self.print_current_datetime()
        self.print_page_subtitle("Selected:")
        self.persons.print_selected_persons()
        print(f"==================== {title} ====================")

    def print_page_subtitle(self, subtitle):
        print(f"---------- {subtitle} ----------")
    def print_contents(self, contents):
        for i, content in enumerate(contents):
            print(f"[{i}]: {content}")
    def get_userinput_index(self, menu_options):
        menu_options_len = len(menu_options)
        self.print_contents(menu_options)
        self.print_page_subtitle("Please Enter Index (Enter '' to go back):")
        user_input = input()
        if (user_input):
            if (user_input.isnumeric()):
                user_input = int(user_input)
            elif not (0 <= user_input < menu_options_len):
                print(f"ERROR: User input ({user_input}) is not a valid index.")
                user_input = None
        else:
            user_input = None
        return user_input
    
    def print_current(self):
        exit_now = False
        if (self.current == "mainmenu"):
            self.print_page_title("MAIN MENU")
            self.print_page_subtitle("Menu:")
            user_input = self.get_userinput_index(self.mainmenu)
            if (user_input is not None):
                self.current = self.mainmenu[user_input]
        elif (self.current == "global_print_menu"):
            self.print_page_title("GLOBAL PRINT MENU")
            user_input = self.get_userinput_index(self.global_print_menu)
            if (user_input is not None):
                self.current = self.global_print_menu[user_input]
                if (self.current == "print_global_active_meetings"):
                    self.print_page_title("PRINT GLOBAL ACTIVE MEETINGS")
                    self.persons.print_global_active_meetings()
                elif (self.current == "print_global_commitments"):
                    self.print_page_title("PRINT GLOBAL COMMITMENTS")
                    self.persons.print_global_commitments()
                elif (self.current == "print_global_meetings"):
                    self.print_page_title("PRINT GLOBAL MEETINGS")
                    self.persons.print_global_meetings()
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "register_person"):
            # role, first_name, last_name, id, id_family, date_registered, date_of_birth, address, phone_number, email, rate, balance, timezone, comments
            items = Functions_User_Register_Ui.register_user()
            if (items):
                self.persons.register_person(items)
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "search"):
            self.print_page_title("SEARCH")
            self.print_page_subtitle("Search Generically For Values (Separated by Space) (Enter '' to go back):")
            user_input = input()
            if (user_input):
                matches = self.persons.search_generically(user_input)
                self.print_page_subtitle(f"Matches [n={len(matches)}]: ")
                self.print_contents(matches)
                if (matches):
                    self.print_page_subtitle(f"Please Enter Indices (Separated by Space) to Add to Selection (Enter '' to go back):")
                    user_input = input()
                    user_input = [x for x in user_input.split(" ")]
                    for x in user_input:
                        if (x.isnumeric()):
                            x = int(x)
                            if (0 <= x < len(matches)):
                                self.persons.append_selected_person(matches[x])
                else:
                    print("No matches found...")
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "search_by_key"):
            self.print_page_title("SEARCH BY KEY")
            self.print_page_subtitle("Person Attributes:")
            self.print_contents(self.persons.person_attributes)
            self.print_page_subtitle("Please Enter Index (Enter '' to go back):")
            user_input = input() 
            if (user_input.isnumeric()):
                match_attr = self.persons.search_for_attr(self.persons.person_attributes[int(user_input)])
                if (match_attr):
                    self.print_page_subtitle(f"[In Attribute '{match_attr}'] Search For Value (Enter '' to go back):")
                    user_input = input()
                    matches = self.persons.search_by_key(match_attr, user_input)
                    self.print_page_subtitle(f"Matches: ")
                    self.print_contents(matches)
                    if (matches):
                        self.print_page_subtitle(f"Please Enter Indices (Separated by Space) to Add to Selection (Enter '' to go back):")
                        user_input = input()
                        if (user_input):
                            user_input = [x for x in user_input.split(" ")]
                            for x in user_input:
                                if (x.isnumeric()):
                                    x = int(x)
                                    if (x in range(len(matches))):
                                        self.persons.append_selected_person(matches[x])
                    else:
                        print("No matches found...")
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "selected_print_menu"):
            self.print_page_title("SELECTED PRINT MENU [For Selected Persons]")
            if (not self.persons.selected_persons):
                print("WARNING: No Selected Persons to Print For. Please Search for & Select Persons First.")
            else:
                user_input = self.get_userinput_index(self.selected_print_menu)
                if (user_input is not None):
                    self.current = self.selected_print_menu[user_input]
                    if (self.current == "print_availability"):
                        self.print_page_title("PRINT AVAILABILITY [For Selected Persons]")
                        for i, person in enumerate(self.persons.selected_persons):
                            self.persons.print_availability(person)
                    elif (self.current == "print_commitments"):
                        self.print_page_title("PRINT COMMITMENTS [For Selected Persons]")
                        for i, person in enumerate(self.persons.selected_persons):
                            self.persons.print_commitments(person)
                    elif (self.current == "print_meetings"):
                        self.print_page_title("PRINT MEETINGS [For Selected Persons]")
                        for i, person in enumerate(self.persons.selected_persons):
                            self.persons.print_meetings(person)
                    elif (self.current == "print_balance_history"):
                        self.print_page_title("PRINT BALANCE HISTORY [For Selected Persons]")
                        for i, person in enumerate(self.persons.selected_persons):
                            self.persons.print_balance_history(person)
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "selected_availability_menu"):
            self.print_page_title("MANAGE AVAILABILITY MENU [For Selected Persons]")
            if (not self.persons.selected_persons):
                print("WARNING: No Selected Persons to Manage Availability For. Please Search for & Select Persons First.")
            else:
                user_input = self.get_userinput_index(self.selected_availability_menu)
                if (user_input is not None):
                    self.current = self.selected_availability_menu[user_input]
                    if (self.current == "print_availability"):
                        self.print_page_title("PRINT AVAILABILITY [For Selected Persons]")
                        for i, person in enumerate(self.persons.selected_persons):
                            self.persons.print_availability(person)
                    elif (self.current == "create_availability"):
                        self.print_page_title("CREATE AVAILABILITY [For Selected Persons]")
                        slots = Functions_Calendar_Ui(self.persons.current_datetime).select_time_slot()
                        for i, person in enumerate(self.persons.selected_persons):
                            for datetime_start_utc, datetime_end_utc in slots:
                                self.persons.create_availability(person, datetime_start_utc, datetime_end_utc)
                    elif (self.current == "remove_availability"):
                        self.print_page_title("REMOVE AVAILABILITIES [For Selected Persons]")
                        for i, person in enumerate(self.persons.selected_persons):
                            self.print_contents(self.persons.get_availability(person))
                            slots_len = len(self.persons.get_availability(person))
                            if (slots_len > 0):
                                self.print_page_subtitle(f"Remove Which Availabilities (Separated by Space)(Enter '' to go back) for: {person.first_name} {person.last_name} #{person.id}: ")
                                user_input = input()
                                user_input = [x for x in user_input.split(" ")]
                                for x in user_input:
                                    if (x.isnumeric()):
                                        x = int(x)
                                        if (0 <= x < slots_len):
                                            self.persons.remove_availability(person, target_index=x)
                            else:
                                print(f"No Availabilities to Remove for: {person.first_name} {person.last_name} #{person.id}...")
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "selected_commitments_menu"):
            self.print_page_title("MANAGE COMMITMENTS MENU [For Selected Persons]")
            if (not self.persons.selected_persons):
                print("WARNING: No Selected Persons to Manage Commitments For. Please Search for & Select Persons First.")
            else:
                user_input = self.get_userinput_index(self.selected_commitments_menu)
                if (user_input is not None):
                    self.current = self.selected_commitments_menu[user_input]
                    if (self.current == "print_commitments"):
                        self.print_page_title("PRINT COMMITMENTS [For Selected Persons]")
                        for i, person in enumerate(self.persons.selected_persons):
                            self.persons.print_commitments(person)
                    elif (self.current == "create_commitments"):
                        self.print_page_title("CREATE COMMITMENTS [For Selected Persons]")
                        slots = Functions_Calendar_Ui(self.persons.current_datetime).select_time_slot()
                        for i, person in enumerate(self.persons.selected_persons):
                            for datetime_start_utc, datetime_end_utc in slots:
                                self.persons.create_commitment(person, datetime_start_utc, datetime_end_utc)
                    elif (self.current == "remove_commitments"):
                        self.print_page_title("REMOVE COMMITMENTS [For Selected Persons]")
                        for i, person in enumerate(self.persons.selected_persons):
                            self.print_contents(self.persons.get_commitments(person))
                            slots_len = len(self.persons.get_commitments(person))
                            if (slots_len > 0):
                                self.print_page_subtitle(f"Remove Which Commitments (Separated by Space)(Enter '' to go back) for: {person.first_name} {person.last_name} #{person.id}: ")
                                user_input = input()
                                user_input = [x for x in user_input.split(" ")]
                                for x in user_input:
                                    if (x.isnumeric()):
                                        x = int(x)
                                        if (0 <= x < slots_len):
                                            self.persons.remove_commitment(person, target_index=x)
                            else:
                                print(f"No Commitments to Remove for: {person.first_name} {person.last_name} #{person.id}...")
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "selected_meetings_menu"):
            self.print_page_title("MANAGE MEETINGS MENU [For Selected Persons]")
            if (not self.persons.selected_persons):
                print("WARNING: No Selected Persons to Manage Meetings For. Please Search for & Select Persons First.")
            else:
                user_input = self.get_userinput_index(self.selected_meetings_menu)
                if (user_input is not None):
                    self.current = self.selected_meetings_menu[user_input]
                    if (self.current == "print_meetings"):
                        self.print_page_title("PRINT MEETINGS [For Selected Persons]")
                        for i, person in enumerate(self.persons.selected_persons):
                            self.persons.print_meetings(person)
                    elif (self.current == "create_meetings"):
                        self.print_page_title("CREATE MEETINGS [For Selected Persons]")
                        slots = Functions_Calendar_Ui(self.persons.current_datetime).select_time_slot()
                        for i, person in enumerate(self.persons.selected_persons):
                            for datetime_start_utc, datetime_end_utc in slots:
                                self.persons.create_meeting(person, datetime_start_utc, datetime_end_utc)
                    elif (self.current == "remove_meetings"):
                        self.print_page_title("REMOVE MEETINGS [For Selected Persons]")
                        for i, person in enumerate(self.persons.selected_persons):
                            self.print_contents(self.persons.get_meetings(person))
                            slots_len = len(self.persons.get_meetings(person))
                            if (slots_len > 0):
                                self.print_page_subtitle(f"Remove Which Meetings (Separated by Space)(Enter '' to go back) for: {person.first_name} {person.last_name} #{person.id}: ")
                                user_input = input()
                                user_input = [x for x in user_input.split(" ")]
                                for x in user_input:
                                    if (x.isnumeric()):
                                        x = int(x)
                                        if (0 <= x < slots_len):
                                            self.persons.remove_meeting(person, target_index=x)
                            else:
                                print(f"No Meetings to Remove for: {person.first_name} {person.last_name} #{person.id}...")
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "find_intersection"):
            self.print_page_title("FIND INTERSECTION [For Selected Persons]")
            intersections = self.persons.get_intersecting_availability()
            self.print_page_subtitle(f"Intersections Found: ")
            self.print_contents(intersections)
            intersections_len = len(intersections)
            if (intersections_len > 0):
                self.print_page_subtitle(f"Please Enter Indices of Intersections to Commit (Enter '' to go back):")
                user_input = input()
                user_input = [x for x in user_input.split(" ")]
                for x in user_input:
                    if (x.isnumeric()):
                        x = int(x)
                        if (0 <= x < intersections_len):
                            self.persons.append_selected_intersection(intersections[x])
                if (self.persons.selected_intersections):
                    self.persons.create_intersecting_commitments()
            else:
                print("No intersections found...")
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "clear_selections"):
            self.print_page_title("CLEAR SELECTIONS (i.e., Selected Persons, Selected Intersections, etc.)")
            self.persons.clear_selections()
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "toggle_debug_outputs"):
            self.print_page_title("TOGGLE DEBUG OUTPUTS")
            self.persons.print_debug = False if (self.persons.print_debug) else True
            self.clear_console = False if (self.persons.print_debug) else True
            print(f"Print Debug Outputs?: {self.persons.print_debug}")
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "exit"):
            exit_now = True
            self.print_page_title("EXIT")
            print("Exiting...")
        return exit_now
    