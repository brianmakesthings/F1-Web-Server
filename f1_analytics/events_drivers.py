from multiprocessing.sharedctypes import Value
import fastf1 as f
import numpy as np
import pandas as pd

# (temp) read in datasets 

df_laps_2021 = pd.read_csv("visualizations/transformed_laps_2021.csv", header=0, index_col=0, parse_dates=["LapStartDate"], infer_datetime_format=True, true_values=["True"], false_values=["False"])
df_laps_2022 = pd.read_csv("visualizations/transformed_laps_2022.csv", header=0, index_col=0, parse_dates=["LapStartDate"], infer_datetime_format=True, true_values=["True"], false_values=["False"])

laps_dfs = {2021:df_laps_2021, 2022:df_laps_2022}

# Getting events list given year is tricky because the 2022 csv is incomplete
# Depend on fastf1's schedule api instead
# Requires: year is 2021 or 2022
# Returns: list of str
def get_event_lists(year):
    
    # returns a fastf1 event schedule object
    df_schedule = f.get_event_schedule(year, include_testing=False)

    return pd.unique(df_schedule["EventName"]).tolist()

# Two versions of the event to drivers function are provided

# The first one uses the laps dataframes only 
# Requires: the event name input is correctly formatted, else an empty list will be returned
# Requires: year is 2021 or 2022
# Returns: list of str (actual driver names)
def event_to_drivers_csv(year, event_name): 
    df_laps = laps_dfs[year]
    df_laps = df_laps[df_laps["EventName"] == event_name][["Team", "Driver"]]
    df_laps["driver_info"] = df_laps["Team"] + df_laps["Driver"]

    # driver_info is a column where team names and driver names are concatenated 
    # first get all the unique combinations as a pandas series, then convert that to a list 
    # sort the list, the behavior is sorting by team name first, then sorting by driver name
    # return the last three characters of each, which is the driver name
    return [i[-3:] for i in sorted(pd.unique(df_laps["driver_info"]).tolist())]

# The second depend on the fastf1 api 
# The event_name input will be fuzzy-matched
# Requires: year is 2021 or 2022
# Returns: list of str (driver numbers)
# AVOID USING THIS AS IT REQUIRES CALLING session.load() WHICH IS BOTH TIME AND SPACE CONSUMING
def event_to_drivers_api(year, event_name):
    race = f.get_event(year, event_name).get_race()
    race.load()
    return race.drivers

### testing 
# print(get_event_lists(2021))
# print(get_event_lists(2022))
# print(event_to_drivers_csv(2022, "French Grand Prix"))
# print(event_to_drivers_csv(2022, "French"))
