from datetime import datetime
from zoneinfo import ZoneInfo

from classes.persons import *
from functions_cmd_ui import *

### Parameters ###
path_to_global_commitments_data = "data\\global_commitments.csv"
path_to_global_meetings_data = "data\\global_meetings.csv"
path_to_person_data = "data\\person.csv"
path_to_person_availability_data = "data\\person_availability.csv"
path_to_person_commitments_data = "data\\person_commitments.csv"
path_to_person_meetings_data = "data\\person_meetings.csv"
path_to_person_balance_history_data = "data\\person_balance_history.csv"

#current_timezone = "UTC"
current_timezone = "America/Toronto"

### Debug ###
# Create logic for student/teacher preferences and auto-grouping to enable auto-scheduling. Only manual input should be availability.
# Update handling of timezones in lower level funcs?
# Make more efficient 'creation of person' - only create if necessary? In case of many many persons.
# Create availability - prevent past detetimes. Sort out logic for commitment -> meeting.

def main():
    print("============================== Create Objects ==============================")
    persons = Persons(path_to_global_commitments_data, path_to_global_meetings_data, path_to_person_data, path_to_person_availability_data, path_to_person_commitments_data, path_to_person_meetings_data, path_to_person_balance_history_data, current_timezone)
    
    print("============================== Init UI ==============================")
    Functions_Cmd_Ui(persons, print_debug=False, clear_console=True)
    
if (__name__ == "__main__"):
    main()