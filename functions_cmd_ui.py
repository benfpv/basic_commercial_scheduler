
import os
from functions_calendar_ui import *
from functions_user_register_ui import *

class Functions_Cmd_Ui(): # DEMO ONLY - this is <ideal design
    def __init__(self, persons, clear_console=True):
        self.persons = persons

        self.current = "mainmenu"
        self.mainmenu = ["print_global_commitments", "print_global_meetings", "register_person", "search", "search_by_key", "print_availability", "create_availability", "remove_availability", "find_intersection", "clear_selections", "toggle_debug_outputs", "exit"]
        
        self.clear_console = clear_console
        
        self.menu_loop()
        
    def menu_loop(self):
        exit_now = False
        while (exit_now == False):
            self.persons.update_current_datetime()
            self.persons.convert_commitments_to_meetings()
            exit_now = self.print_current()
        
    def print_page_title(self, title):
        if (self.clear_console):
            os.system("cls") if (os.name == "nt") else os.system("clear")
        print(f"==================== {title} ====================")
    def print_page_subtitle(self, subtitle):
        print(f"---------- {subtitle} ----------")
    def print_contents(self, contents):
        for i, content in enumerate(contents):
            print(f"[{i}]: {content}")
    
    def print_current(self):
        exit_now = False
        if (self.current == "mainmenu"):
            self.print_page_title("MAIN MENU")
            print(f"Current Datetime (as of): {self.persons.current_datetime}")
            self.print_page_subtitle("Selected:")
            self.persons.print_selected_persons()
            self.print_page_subtitle("Menu:")
            self.print_contents(self.mainmenu)
            self.print_page_subtitle("Please Enter Index:")
            user_input = input()
            if (user_input.isnumeric()):
                user_input = int(user_input)
                if (user_input in range(len(self.mainmenu))):
                    self.current = self.mainmenu[user_input]
        elif (self.current == "print_global_commitments"):
            self.print_page_title("PRINT GLOBAL COMMMITMENTS")
            self.persons.print_global_commitments()
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
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
                            if (x in range(len(matches))):
                                self.persons.append_selected_person(matches[x])
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "search_by_key"):
            self.print_page_title("SEARCH BY KEY")
            self.print_page_subtitle("Person Attributes:")
            self.print_contents(self.persons.person_attributes)
            self.print_page_subtitle("Please Enter Index:")
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
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "print_availability"):
            self.print_page_title("PRINT AVAILABILITY [For Selected Persons]")
            for i, person in enumerate(self.persons.selected_persons):
                self.persons.print_availability(person)
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "create_availability"):
            self.print_page_title("CREATE AVAILABILITY [For Selected Persons]")
            slots = Functions_Calendar_Ui(self.persons.current_datetime).select_time_slot()
            for i, person in enumerate(self.persons.selected_persons):
                for datetime_start_utc, datetime_end_utc in slots:
                    self.persons.create_availability(person, datetime_start_utc, datetime_end_utc)
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "remove_availability"):
            self.print_page_title("REMOVE AVAILABILITY [For Selected Persons]")
            slots = Functions_Calendar_Ui(self.persons.current_datetime).select_time_slot()
            for i, person in enumerate(self.persons.selected_persons):
                for datetime_start_utc, datetime_end_utc in slots:
                    self.persons.remove_availability(person, datetime_start_utc, datetime_end_utc)
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "find_intersection"):
            self.print_page_title("FIND INTERSECTION [For Selected Persons]")
            intersections = self.persons.get_intersecting_availability()
            self.print_page_subtitle(f"Intersections Found: ")
            self.print_contents(intersections)
            if (intersections):
                self.print_page_subtitle(f"Please Enter Indices of Intersections to Commit (Enter '' to go back):")
                user_input = input()
                user_input = [x for x in user_input.split(" ")]
                for x in user_input:
                    if (x.isnumeric()):
                        x = int(x)
                        if (x in range(len(intersections))):
                            self.persons.append_selected_intersection(intersections[x])
                if (self.persons.selected_intersections):
                    self.persons.create_intersecting_commitments()
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
            print(f"Print Debug Outputs?: {self.persons.print_debug}")
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "exit"):
            exit_now = True
        return exit_now
    