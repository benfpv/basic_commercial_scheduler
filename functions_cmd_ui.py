
from functions_calendar_ui import *
from functions_user_register_ui import *

class Functions_Cmd_Ui():
    def __init__(self, persons, current_datetime):
        self.persons = persons
        self.current_datetime = current_datetime
        
        self.current = "mainmenu"
        self.mainmenu = ["print_selected", "print_global_commitments", "register_person", "search", "search_by_key", "print_availability", "create_availability", "remove_availability", "find_intersection", "clear_working_memory", "exit"]
        
        self.menu_loop()
        
    def menu_loop(self):
        exit_now = False
        while (exit_now == False):
            exit_now = self.print_current()
        
    def print_page_title(self, title):
        print(f"==================== {title} ====================")
    def print_page_subtitle(self, subtitle):
        print(f"---------- {subtitle} ----------")
    def print_contents(self, contents):
        for i, content in enumerate(contents):
            print(f"[{i}]: {content}")
    
    def print_current(self):
        exit_now = False
        break_to_mainmenu = False
        if (self.current == "mainmenu"):
            self.print_page_title("MAIN MENU")
            self.print_contents(self.mainmenu)
            user_input = " "
            while (user_input != "") and (not break_to_mainmenu):
                self.print_page_subtitle("Please Enter Index:")
                user_input = input()
                if (user_input.isnumeric()):
                    user_input = int(user_input)
                    if (user_input in range(len(self.mainmenu))):
                        self.current = self.mainmenu[user_input]
                        break_to_mainmenu = True
                        break
        elif (self.current == "print_global_commitments"):
            self.print_page_title("PRINT GLOBAL COMMMITMENTS")
            self.persons.print_global_commitments()
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "print_selected"):
            self.print_page_title("PRINT SELECTED")
            self.persons.print_selected()
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
            user_input = " "
            while (user_input != "") and (not break_to_mainmenu):
                self.print_page_subtitle("Search Generically For Values (Separated by Space) (Enter '' to go back):")
                user_input = input()
                if (user_input):
                    matches = self.persons.search_generically(user_input)
                    self.print_page_subtitle(f"Matches [n={len(matches)}]: ")
                    self.print_contents(matches)
                    if (matches):
                        while (user_input != "") and (not break_to_mainmenu):
                            self.print_page_subtitle(f"Please Enter Indices (Separated by Space) to Add to Selection (Enter '' to go back):")
                            user_input = input()
                            user_input = [x for x in user_input.split(" ")]
                            for x in user_input:
                                if (x.isnumeric()):
                                    x = int(x)
                                    if (x in range(len(matches))):
                                        self.persons.append_selected(matches[x])
                            break_to_mainmenu = True
                            break
                    else:
                        break_to_mainmenu = True
                        break
                else:
                    break_to_mainmenu = True
                    break
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "search_by_key"):
            self.print_page_title("SEARCH BY KEY")
            user_input = " "
            while (user_input != "") and (not break_to_mainmenu):
                self.print_page_subtitle("Enter Attribute Key (e.g., first_name, last_name, id, family_id, etc.) (Enter '' to go back):")
                user_input = input()
                match_attr = self.persons.search_for_attr(user_input)
                if (match_attr):
                    while (user_input != "") and (not break_to_mainmenu):
                        self.print_page_subtitle(f"[In Attribute '{match_attr}'] Search For Value (Enter '' to go back):")
                        user_input = input()
                        matches = self.persons.search_by_key(match_attr, user_input)
                        self.print_page_subtitle(f"Matches: ")
                        self.print_contents(matches)
                        if (matches):
                            while (user_input != "") and (not break_to_mainmenu):
                                self.print_page_subtitle(f"Please Enter Indices (Separated by Space) to Add to Selection (Enter '' to go back):")
                                user_input = input()
                                user_input = [x for x in user_input.split(" ")]
                                for x in user_input:
                                    if (x.isnumeric()):
                                        x = int(x)
                                        if (x in range(len(matches))):
                                            self.persons.append_selected(matches[x])
                                break_to_mainmenu = True
                                break
                        else:
                            break_to_mainmenu = True
                            break
                else:
                    break_to_mainmenu = True
                    break
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "print_availability"):
            self.print_page_title("PRINT AVAILABILITY [For Selected]")
            for i, person in enumerate(self.persons.selected):
                self.persons.print_availability(person)
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "create_availability"):
            self.print_page_title("CREATE AVAILABILITY [For Selected]")
            slots = Functions_Calendar_Ui(self.current_datetime).select_time_slot()
            for i, person in enumerate(self.persons.selected):
                for datetime_start_utc, datetime_end_utc in slots:
                    self.persons.create_availability(person, datetime_start_utc, datetime_end_utc)
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "remove_availability"):
            self.print_page_title("REMOVE AVAILABILITY [For Selected]")
            slots = Functions_Calendar_Ui(self.current_datetime).select_time_slot()
            for i, person in enumerate(self.persons.selected):
                for datetime_start_utc, datetime_end_utc in slots:
                    self.persons.remove_availability(person, datetime_start_utc, datetime_end_utc)
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "find_intersection"):
            self.print_page_title("FIND INTERSECTION [For Selected]")
            intersections = self.persons.get_intersecting_availability()
            self.print_page_subtitle(f"Intersections: ")
            self.print_contents(intersections)
            if (intersections):
                user_input = " "
                while (user_input != "") and (not break_to_mainmenu):
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
                    break_to_mainmenu = True
                    break
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "clear_working_memory"):
            self.print_page_title("CLEAR WORKING MEMORY (i.e., Selected Persons, Intersections, etc.)")
            self.persons.clear_working_memory()
            self.current = "mainmenu"
            user_input = input("...Press Enter to Continue...")
        elif (self.current == "exit"):
            exit_now = True
        return exit_now
    