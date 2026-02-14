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

default_timezone = ZoneInfo("UTC")
current_datetime = datetime.now(default_timezone)

### Debug ###
# Make more efficient 'creation of person' - only create if necessary? In case of many many persons.
# Consider possible commitments_locked_in or similar, after commitment is made, but before actual meeting, in case of urgent cancels etc.
# Do convert commitments to meetings etc.

def main():
    print("============================== Create Objects ==============================")
    persons = Persons(path_to_global_commitments_data, path_to_global_meetings_data, path_to_person_data, path_to_person_availability_data, path_to_person_commitments_data)
    
    print("============================== Init UI ==============================")
    Functions_Cmd_Ui(persons, current_datetime)
    
if (__name__ == "__main__"):
    main()