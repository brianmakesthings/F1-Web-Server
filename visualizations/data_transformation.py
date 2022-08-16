# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import fastf1 as f
# import import_ipynb

# %%
f.Cache.enable_cache("./f1_cache")

# # %% [markdown]
# # ## Load Dataframes

# # %%
df_laps_2021 = pd.read_csv("./visualizations/all_laps_2021.csv", parse_dates=["LapStartDate"], infer_datetime_format=True, index_col=0, header=0, true_values=["True"], false_values=["False"])
df_laps_2022 = pd.read_csv("./visualizations/all_laps_2022.csv", parse_dates=["LapStartDate"], infer_datetime_format=True, index_col=0, header=0, true_values=["True"], false_values=["False"])

# # %%
df_laps_2021[["Time", "LapTime", "PitInTime", "PitOutTime", "Sector1Time", "Sector2Time", "Sector3Time", "Sector1SessionTime", "Sector2SessionTime", "Sector3SessionTime", "LapStartTime"]] = df_laps_2021[["Time", "LapTime", "PitInTime", "PitOutTime", "Sector1Time", "Sector2Time", "Sector3Time", "Sector1SessionTime", "Sector2SessionTime", "Sector3SessionTime", "LapStartTime"]].apply(pd.to_timedelta)
df_laps_2022[["Time", "LapTime", "PitInTime", "PitOutTime", "Sector1Time", "Sector2Time", "Sector3Time", "Sector1SessionTime", "Sector2SessionTime", "Sector3SessionTime", "LapStartTime"]] = df_laps_2022[["Time", "LapTime", "PitInTime", "PitOutTime", "Sector1Time", "Sector2Time", "Sector3Time", "Sector1SessionTime", "Sector2SessionTime", "Sector3SessionTime", "LapStartTime"]].apply(pd.to_timedelta)

# # %% [markdown]
# # ## Global Variables

# # %%
num_rounds_2021 = df_laps_2021["RoundNumber"].nunique()
num_rounds_2022 = df_laps_2022["RoundNumber"].nunique()

# # %% [markdown]
# # ## Data Transformation

# # %% [markdown]
# # ### Add Tyre Information Columns

# # %%
# df_laps_2021["IsSlick"] = df_laps_2021.apply(lambda row: row.loc["Compound"] in ["SOFT", "MEDIUM", "HARD"], axis=1)
# df_laps_2022["IsSlick"] = df_laps_2022.apply(lambda row: row.loc["Compound"] in ["SOFT", "MEDIUM", "HARD"], axis=1)

# # %% [markdown]
# # FastF1 provides relative compound information (soft, medium, hard) as the `Compound` column in its `Laps` objects
# # 
# # The actual compound names (C1, C2, C3, C4, C5) needs to be added to main consistency. These will be recorded in the `CompoundName` column.
# # 
# # Intermediate compound is denoted by `CompoundName = 6`. Wet Compound is denoted by `CompoundName = 7`. 
# # 
# # Compound selection logged as `RoundNumber: [soft_compound, medium_compound, hard_compound]` pairs

# # %%
# # 2021 compound selection 
# # Source: https://press.pirelli.com/2021-tyre-compound-choices/

compound_selection_2021 = {1:[2,3,4],
                           2:[2,3,4],
                           3:[1,2,3],
                           4:[1,2,3],
                           5:[3,4,5],
                           6:[3,4,5],
                           7:[3,4,5],
                           8:[2,3,4],
                           9:[2,3,4],
                           10:[1,2,3],
                           11:[2,3,4],
                           12:[2,3,4],
                           13:[1,2,3],
                           14:[2,3,4],
                           15:[3,4,5],
                           16:[3,4,5],
                           17:[1,2,3],
                           18:[2,3,4],
                           19:[2,3,4],
                           20:[2,3,4],
                           21:[2,3,4],
                           22:[2,3,4],
                           23:[3,4,5]}

# # %%
# # 2022 compound selection 
# # Source: https://press.pirelli.com/2022-tyre-compound-choices--bahrain-saudi-arabia-australia/
# #         (Bahrain, Saudi, Australia)
# #         https://press.pirelli.com/2022-tyre-compound-choices--emilia-romagna-miami-spain-monaco/
# #         (Imola, Miami, Spain, Monaco)
# #         https://press.pirelli.com/2022-azerbaijan-grand-prix--preview/
# #         (Azerbaijian)
# #         https://press.pirelli.com/2022-canada-grand-prix---preview/
# #         (Canada)
# #         https://www.formula1.com/en/latest/article.what-tyres-will-the-teams-and-drivers-have-for-the-2022-british-grand-prix.5NSQn3DvP84qUkQIqltoxd.html
# #         (Silverstone)
# #         https://press.pirelli.com/2022-austrian-grand-prix---preview/
# #         (Austria)
# #         https://press.pirelli.com/2022-french-grand-prix--preview/
# #         (France)
# #         https://press.pirelli.com/2022-hungarian-grand-prix---preview/
# #         (Hungary)

compound_selection_2022 = {1:[1,2,3],
                           2:[3,4,5],
                           3:[2,3,5],
                           4:[2,3,4],
                           5:[2,3,4],
                           6:[1,2,3],
                           7:[3,4,5],
                           8:[3,4,5],
                           9:[3,4,5],
                           10:[1,2,3],
                           11:[3,4,5],
                           12:[2,3,4],
                           13:[2,3,4]
                          }

# # %%
# def compound_relative_to_absolute(row, year):  
#     compound_to_index = {"SOFT":2, "MEDIUM":1, "HARD":0}
    
#     if row.loc["Compound"] not in compound_to_index:
#         return row.loc["Compound"]
#     else:
#         if year == 2021:
#             if row.loc["Compound"] in compound_to_index:
#                 return 'C' + str(compound_selection_2021[row.loc["RoundNumber"]][compound_to_index[row.loc["Compound"]]])
#             else: 
#                 return np.nan
#         elif year == 2022:
#             if row.loc["Compound"] in compound_to_index:
#                 return 'C' + str(compound_selection_2022[row.loc["RoundNumber"]][compound_to_index[row.loc["Compound"]]])
#             else:
#                 return np.nan
#         else:
#             raise ValueError("Year requested ({}) not available".format(year))

# # %%
# df_laps_2021["CompoundName"] = df_laps_2021.apply(lambda row: compound_relative_to_absolute(row, 2021), axis=1)
# df_laps_2022["CompoundName"] = df_laps_2022.apply(lambda row: compound_relative_to_absolute(row, 2022), axis=1)

# # %% [markdown]
# # ### Add Relative Timing Columns
# # 

# # %% [markdown]
# # A "representative lap time" for the session is calculated by finding the median of the laps that meet the following condition:
# # 
# # - Raced on slick tyres (`IsSlick = True`) (This definition is optional)
# # - `IsAccurate = True`, see definition [here](https://theoehrly.github.io/Fast-F1/core.html#fastf1.core.Laps)
# # - Is completed under green flag (`TrackStatus == 1`), note that this definition is stricter than the one used for `IsAccurate`
# # 
# # Define "valid laps" as the laps that meet all above conditions. This is recorded in the new `IsValid` column.
# # 
# # The representative lap time for each session is recorded in the `RepTime` column.
# # 
# # The fastest lap time for the session is the fastest time out of the laps where `IsPersonalBest = True` ([definition](https://theoehrly.github.io/Fast-F1/core.html#laps)). Note that this is the same definiton used by the FastF1 `pick_fastest()` method.
# # 
# # Using these two times as benchmarks, the following columns are added:
# # 
# # - `DeltaToRep`
# # - `DeltaToFastest`
# # - `PctFromRep`
# # - `PctFromFastest`
# # - `SDFromRep` (Standard deviation calculated using valid laps only)
# # 
# # The fastest lap time for each session is recorded in the `FastestTime` column.
# # 
# # Caveat: The 2021 Turkish Grand Prix only has 1 valid lap, rendering these columns inaccurate. This is not a problem as 2021 Turkish Grand Prix is not a subject of interest for this analysis due to the same reason. All other sessions have at least 600 valid laps.

# # %%
def check_lap_valid(row):
    return row.loc["IsSlick"] and row.loc["IsAccurate"] and row.loc["TrackStatus"] == 1

# # %%
# df_laps_2021["IsValid"] = df_laps_2021.apply(lambda row: check_lap_valid(row), axis=1)
# df_laps_2022["IsValid"] = df_laps_2022.apply(lambda row: check_lap_valid(row), axis=1)

# # %%
# rep_times_2021 = {i:df_laps_2021[(df_laps_2021["RoundNumber"]==i) & (df_laps_2021["IsValid"]==True)]["LapTime"].median(numeric_only=False) for i in range(1, num_rounds_2021+1)}
# rep_times_2022 = {i:df_laps_2022[(df_laps_2022["RoundNumber"]==i) & (df_laps_2022["IsValid"]==True)]["LapTime"].median(numeric_only=False) for i in range(1, num_rounds_2021+1)}

# # %%
# fastest_times_2021 = {i:df_laps_2021[(df_laps_2021["RoundNumber"]==i) & (df_laps_2021["IsPersonalBest"] == True)]["LapTime"].min(numeric_only=False) for i in range(1, num_rounds_2021+1)}
# fastest_times_2022 = {i:df_laps_2022[(df_laps_2022["RoundNumber"]==i) & (df_laps_2022["IsPersonalBest"] == True)]["LapTime"].min(numeric_only=False) for i in range(1, num_rounds_2022+1)}

# # %%
# df_laps_2021["DeltaToRep"] = df_laps_2021.apply(lambda row: row.loc["LapTime"] - rep_times_2021[row.loc["RoundNumber"]], axis=1)
# df_laps_2022["DeltaToRep"] = df_laps_2022.apply(lambda row: row.loc["LapTime"] - rep_times_2022[row.loc["RoundNumber"]], axis=1)

# # %%
# df_laps_2021["DeltaToFastest"] = df_laps_2021.apply(lambda row: row.loc["LapTime"] - fastest_times_2021[row.loc["RoundNumber"]], axis=1)
# df_laps_2022["DeltaToFastest"] = df_laps_2022.apply(lambda row: row.loc["LapTime"] - fastest_times_2022[row.loc["RoundNumber"]], axis=1)

# # %%
# df_laps_2021["PctFromRep"] = df_laps_2021.apply(lambda row: round(row.loc["DeltaToRep"] / rep_times_2021[row.loc["RoundNumber"]] *100, 3), axis=1)
# df_laps_2022["PctFromRep"] = df_laps_2022.apply(lambda row: round(row.loc["DeltaToRep"] / rep_times_2022[row.loc["RoundNumber"]] *100, 3), axis=1)

# # %%
# df_laps_2021["PctFromFastest"] = df_laps_2021.apply(lambda row: round(row.loc["DeltaToFastest"] / fastest_times_2021[row.loc["RoundNumber"]] *100, 3), axis=1)
# df_laps_2022["PctFromFastest"] = df_laps_2022.apply(lambda row: round(row.loc["DeltaToFastest"] / fastest_times_2022[row.loc["RoundNumber"]] *100, 3), axis=1)

# # %% [markdown]
# # Track evolution has a significant influence on lap times. As the most significant confounding variable that impacts all lap times, we must control for it. 
# # 
# # Two columns will be added for this purpose:
# # 
# # - `DeltaToLapRep`
# # - `PctFromLapRep`
# # 
# # The definition for the per lap representative lap times is the same as the definition for the event representative lap time.

# # %%
# lap_reps_2021 = {}
# lap_reps_2022 = {}

# for round_number in pd.unique(df_laps_2021["RoundNumber"]):
#     event_laps = df_laps_2021[df_laps_2021["RoundNumber"] == round_number]
#     lap_numbers = pd.unique(event_laps["LapNumber"])
#     event_laps = event_laps[event_laps["IsValid"]==True]
#     event_lap_reps = {}
    
#     for lap in lap_numbers:
#         event_lap_reps[lap] = event_laps[event_laps["LapNumber"] == lap]["LapTime"].median()
    
#     lap_reps_2021[round_number] = event_lap_reps
    
# for round_number in pd.unique(df_laps_2022["RoundNumber"]):
#     event_laps = df_laps_2022[df_laps_2022["RoundNumber"] == round_number]
#     lap_numbers = pd.unique(event_laps["LapNumber"])
#     event_laps = event_laps[event_laps["IsValid"]==True]    
#     event_lap_reps = {}
    
#     for lap in lap_numbers:
#         event_lap_reps[lap] = event_laps[event_laps["LapNumber"] == lap]["LapTime"].median()
    
#     lap_reps_2022[round_number] = event_lap_reps

# # %%
# df_laps_2021["DeltaToLapRep"] = df_laps_2021.apply(lambda row: row.loc["LapTime"] - lap_reps_2021[row.loc["RoundNumber"]][row.loc["LapNumber"]], axis=1)
# df_laps_2022["DeltaToLapRep"] = df_laps_2022.apply(lambda row: row.loc["LapTime"] - lap_reps_2022[row.loc["RoundNumber"]][row.loc["LapNumber"]], axis=1)

# # %%
# df_laps_2021["PctFromLapRep"] = df_laps_2021.apply(lambda row: round(row.loc["DeltaToLapRep"] / lap_reps_2021[row.loc["RoundNumber"]][row.loc["LapNumber"]] * 100, 3), axis=1)
# df_laps_2022["PctFromLapRep"] = df_laps_2022.apply(lambda row: round(row.loc["DeltaToLapRep"] / lap_reps_2022[row.loc["RoundNumber"]][row.loc["LapNumber"]] * 100, 3), axis=1)

# # %% [markdown]
# # ## Export To CSV

# # %%
# df_laps_2021.columns

# # %%
# df_laps_2021.to_csv("transformed_laps_2021.csv")
# df_laps_2022.to_csv("transformed_laps_2022.csv")


