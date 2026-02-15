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

#current_timezone = ZoneInfo("UTC")
current_timezone = ZoneInfo("America/Toronto")

### Debug ###
# Make more efficient 'creation of person' - only create if necessary? In case of many many persons.
# Consider meetings in-progress recording as well!
# Convert data structures to pd?

def main():
    print("============================== Create Objects ==============================")
    persons = Persons(current_timezone, path_to_global_commitments_data, path_to_global_meetings_data, path_to_person_data, path_to_person_availability_data, path_to_person_commitments_data, path_to_person_meetings_data)
    
    print("============================== Init UI ==============================")
    Functions_Cmd_Ui(persons, True)
    
if (__name__ == "__main__"):
    main()