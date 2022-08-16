# %% [markdown]
# # Imports and Global Variables

# %%
import numpy as np
import pandas as pd 
import fastf1 as f
import fastf1.plotting as p
from matplotlib import rcParams, pyplot as plt
import seaborn as sns 
# import import_ipynb
from math import ceil
import mpld3

# %%
f.Cache.enable_cache("./f1_cache")

# %%
from .data_transformation import compound_selection_2021, compound_selection_2022, num_rounds_2021, num_rounds_2022

# %%
slick_tyre_names = ["SOFT", "MEDIUM", "HARD"]

relative_compound_palette = {"SOFT":"#da291c", "MEDIUM":"#fed12e", "HARD":"#eeeeea", "INTERMEDIATE":"#43b02a", "WET":"#0166ac", "UNKNOWN":"#40e040"}
relative_compound_markers = {"SOFT":'o', "MEDIUM":'^', "HARD":'s', "INTERMEDIATE":'P', "WET":'X', "UNKNOWN":'.'}
relative_compound_labels = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]

# The absolute_compound_palette uses the 2018 colors in order of ultrasoft to hard
absolute_compound_palette = {'C1':"#00a2f3", 'C2': "#eeeeea", 'C3': "#fed12e", 'C4':"#da291c", 'C5':"#b24ba7", "INTERMEDIATE":"#43b02a", "WET":"#0166ac"}
absolute_compound_markers = {'C1':"P", "C2":'s', "C3":'^', "C4":'o', "C5":'D', "INTERMEDIATE":'P', "WET":'X', "UNKNOWN":'.'}
absolute_compound_labels = ["C1", "C2", "C3", "C4", "C5", "INTERMEDIATE", "WET"]

FreshTyre_markers = {True:'o', False:'X'}

# %%
sns.set(rc={"figure.dpi":300, 'savefig.dpi':300})

# %% [markdown]
# # Load Dataframes 

# %%
df_schedule_2021 = f.get_event_schedule(2021)
df_schedule_2022 = f.get_event_schedule(2022)

# %%
df_laps_2021 = pd.read_csv("./visualizations/transformed_laps_2021.csv", header=0, index_col=0, parse_dates=["LapStartDate"], infer_datetime_format=True, true_values=["True"], false_values=["False"])
df_laps_2022 = pd.read_csv("./visualizations/transformed_laps_2022.csv", header=0, index_col=0, parse_dates=["LapStartDate"], infer_datetime_format=True, true_values=["True"], false_values=["False"])

# %%
df_laps_2021[["Time", "LapTime", "PitInTime", "PitOutTime", "Sector1Time", "Sector2Time", "Sector3Time", "Sector1SessionTime", "Sector2SessionTime", "Sector3SessionTime", "LapStartTime", "DeltaToRep", "DeltaToFastest", "DeltaToLapRep"]] = df_laps_2021[["Time", "LapTime", "PitInTime", "PitOutTime", "Sector1Time", "Sector2Time", "Sector3Time", "Sector1SessionTime", "Sector2SessionTime", "Sector3SessionTime", "LapStartTime", "DeltaToRep", "DeltaToFastest", "DeltaToLapRep"]].apply(pd.to_timedelta)
df_laps_2022[["Time", "LapTime", "PitInTime", "PitOutTime", "Sector1Time", "Sector2Time", "Sector3Time", "Sector1SessionTime", "Sector2SessionTime", "Sector3SessionTime", "LapStartTime", "DeltaToRep", "DeltaToFastest", "DeltaToLapRep"]] = df_laps_2022[["Time", "LapTime", "PitInTime", "PitOutTime", "Sector1Time", "Sector2Time", "Sector3Time", "Sector1SessionTime", "Sector2SessionTime", "Sector3SessionTime", "LapStartTime", "DeltaToRep", "DeltaToFastest", "DeltaToLapRep"]].apply(pd.to_timedelta)


# %% [markdown]
# # Visualization Functions

# %% [markdown]
# ## Tyre Usage

# %%
def prep_events_list(year, events):
    # Process a list of events and return a list of corresponding round numbers
    
    for index, event in enumerate(events):
        if isinstance(event, str):
            if event.isdigit():
                events[index] = int(event)
            else:
                events[index] = f.get_event(year, event)["RoundNumber"]
        elif not isinstance(event, int):
            raise TypeError("{} not accepted. The valid types are int and str".format(type(event)))
    return events

# %%
def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.1f}%  ({v:d})'.format(p=pct,v=val)
    return my_autopct

# %%
def tyre_usage_pie(year, title=None, events=None, drivers=None, slick_only=False, absolute_compound=False):
    
    """
    Make tyre usage pie chart that allows filtering by events, drivers, and slick vs wet tyres
    
    Args:
        year: int {2021, 2022}
            Championship year
        
        title: str, default:None
            
        events: list, default: None
            A list containing the round number (as either int or string) or the names of events
            e.g. [1, "Hungary", "5", "British Grand Prix", "Monza"]
            Name fuzzy matching provided by fastf1.get_event()
            Using the default value will select all events
            
        drivers: list, default:None
            A list containing three-letter driver abbreviations 
            e.g. ["VER", "HAM"]
            Using the default value will select all drivers
            
        slick_only: bool, default:False
            If true, only laps raced on slick tyres are counted
            If false, all laps (with known tyre compound) are counted
            
        absolute_compound: bool, default:False
            If true, group tyres by their absolute compound names (C1, C2 etc.)
            If false, group tyres by their names in the respective events (SOFT, MEDIUM, HARD)
          (Wet and Intermediate tyres unaffected)
          
    Returns: No return values
    """    
    included_laps = pd.DataFrame()
    
    if year == 2021:
        included_laps = df_laps_2021
    elif year == 2022:
        included_laps = df_laps_2022
    else:
        raise ValueError("Year requested ({}) not available".format(year))
    
    if events is None:
        events = pd.unique(included_laps["RoundNumber"])
    else:
        events = prep_events_list(year, events)
        
    if drivers is None:
        drivers = pd.unique(included_laps["DriverNumber"])

    if slick_only:
        included_laps = included_laps[included_laps["IsSlick"] == True]
    else:
        included_laps = included_laps[pd.notnull(included_laps["Compound"])]  
    
    included_laps = included_laps[(included_laps["RoundNumber"].isin(events)) & (included_laps["Driver"].isin(drivers))]
    
    fig, ax = plt.subplots(figsize=(10,6))
    plt.style.use("default")
    
    if absolute_compound:
        labels = absolute_compound_labels
        lap_counts = included_laps.groupby("CompoundName").count()
        palette = absolute_compound_palette.values()

        # Driver column is used because it is not nullable and therefore holds the correct count
        counts = [lap_counts.loc[i]["Driver"] if i in lap_counts.index else 0 for i in labels]
        
        wedges, texts, autotexts = ax.pie(x=counts, 
                                          labels=None, 
                                          colors=palette, 
                                          autopct=make_autopct(counts), 
                                          counterclock=False, 
                                          startangle=90)
    else:
        labels = relative_compound_labels
        lap_counts = included_laps.groupby("Compound").count()
        palette = relative_compound_palette.values()
        counts = [lap_counts.loc[i]["Driver"] if i in lap_counts.index else 0 for i in labels]
        
        wedges, texts, autotexts = ax.pie(x=counts, 
                                          labels=None, 
                                          colors=palette, 
                                          autopct=make_autopct(counts), 
                                          counterclock=False, 
                                          startangle=90)

    ax.legend(labels=labels, title="Compound Names", loc="center right")
    ax.axis("equal")
    ax.set_title(title)
    plt.setp(autotexts, size=12)
    # plt.show()
    

# %% [markdown]
# ## Lap Time Scatterplot

# %% [markdown]
# ### Add second columns

# %% [markdown]
# Timedelta objects are hard to make visualizations with. Three new columns that store the seconds equivalence of timedelta will be created to address this issue. These new columns are denoted with a lower case s at the beginning.
# 
# - `sLapTime`
# - `sDeltaToRep`
# - `sDeltaToFastest`
# - `sDeltaToLapRep`

# %%
df_laps_2021["sLapTime"] = df_laps_2021.apply(lambda row: row.loc["LapTime"].total_seconds(), axis=1)
df_laps_2022["sLapTime"] = df_laps_2022.apply(lambda row: row.loc["LapTime"].total_seconds(), axis=1)

# %%
df_laps_2021["sDeltaToRep"] = df_laps_2021.apply(lambda row: row.loc["DeltaToRep"].total_seconds(), axis=1)
df_laps_2022["sDeltaToRep"] = df_laps_2022.apply(lambda row: row.loc["DeltaToRep"].total_seconds(), axis=1)

# %%
df_laps_2021["sDeltaToFastest"] = df_laps_2021.apply(lambda row: row.loc["DeltaToFastest"].total_seconds(), axis=1)
df_laps_2022["sDeltaToFastest"] = df_laps_2022.apply(lambda row: row.loc["DeltaToFastest"].total_seconds(), axis=1)

# %%
df_laps_2021["sDeltaToLapRep"] = df_laps_2021.apply(lambda row: row.loc["DeltaToLapRep"].total_seconds(), axis=1)
df_laps_2022["sDeltaToLapRep"] = df_laps_2022.apply(lambda row: row.loc["DeltaToLapRep"].total_seconds(), axis=1)

# %% [markdown]
# ### Lap Times by Event and Drivers

# %%
def lap_filter_round_driver(row, round_number, drivers):
    """
    Filtering logic for rows to be included in plot_driver_lap_times() plots
    
    Filter for round number and drivers only so pitstops can be identified later   
    """
    
    return row.loc["RoundNumber"] == round_number and row.loc["Driver"] in drivers 

# %%
def lap_filter_upper_accurate(row, upper_bound):
    """
    Additional filtering lofic for rows to be included in plot_driver_lap_times() plots
    
    Filter for IsAccurate and upper bound
    """
    
    if upper_bound is None:
        upper_bound = 50
    
    return row.loc["PctFromFastest"] < upper_bound and row.loc["IsAccurate"]

# %%
def plot_args(absolute_compound):
    """
    Given the input arguments, return a list of the corresponding arguments to be supplied to the plotting function
    
    Returns: tuple
        (hue, palette, marker, labels)
    """    
    if absolute_compound:
        return ("CompoundName", absolute_compound_palette, absolute_compound_markers, absolute_compound_labels)
    else:
        return ("Compound", relative_compound_palette, relative_compound_markers, relative_compound_labels)

# %%
def reorder_legend(labels):
    """
    Given the list of labels, return a list of int that specifies their appropriate order in the legend
    
    e.g. labels = ["MEDIUM", "HARD", "SOFT"]
         desired = ["SOFT", "MEDIUM", "HARD"]
         return [2, 0, 1]
         
         labels = ["C3", "C1", "WET"]
         desired = ["C1", "C3", "WET"],
         return [1, 0, 2]
    """
    
    order = []
    old_indices = list(range(len(labels)))
    
    if "SOFT" in labels or "MEDIUM" in labels or "HARD" in labels:
        pos = [relative_compound_labels.index(label) if label in relative_compound_labels else -1 for label in labels]
        order = [old_index for sorted_index, old_index in sorted(zip(pos, old_indices))]
    else:
        pos = [absolute_compound_labels.index(label) if label in absolute_compound_labels else -1 for label in labels]
        order = [old_index for sorted_index, old_index in sorted(zip(pos, old_indices))]
    
    return order


# %%
def plot_driver_lap_times(year, event, drivers, y, upper_bound=10, absolute_compound=False):
    """
    Plot lap times for selected year, event, and drivers
    
    Only laps with IsAccurate=True will be plotted.
        
    Args:
        year: int {2021, 2022}
            Championship year
            
        event: int or str
            Round number or name of the event
            Name is fuzzy matched by fastf1.get_event()
        
        drivers: list
            List of the three-letter abbreviations of the drivers to be included 
            
        y: str, default
            Name of the column to be used as the y-axis.
            
        upper_bound: float, default: 10
            The upper bound of PctFromFastest for the laps to include
            
            If None, upper bound is set to 30. Use this setting for wet races!
            
            e.g. By default, only laps that are no more than 10% slower than the fastest lap are plotted 
        
        absolute_compound: bool, default: False
            If True, use absolute compound palette (C1, C2 etc.)
            
            If False, use relative compound palette (SOFT, MEDIUM, HARD)
        
    Returns: Figure
    """    
    
    max_width = 4
    
    plt.style.use("dark_background")
    
    fontdict = {'fontsize': rcParams['axes.titlesize'],
                'fontweight': rcParams['axes.titleweight'],
                'color': rcParams['axes.titlecolor'],
                'verticalalignment': 'baseline',
                'horizontalalignment': "center"}
    
    num_row = ceil(len(drivers) / max_width)
    num_col = len(drivers) if len(drivers) < max_width else max_width
    fig, axes = plt.subplots(nrows=num_row, ncols=num_col, sharey=True, sharex=True, figsize=(5*num_col, 5*num_row))
    
    # Prevent TypeError when only one driver is plotted
    if len(drivers) == 1:
        axes = np.array([axes])

    event_info = f.get_event(year, event)
    round_number = event_info["RoundNumber"]
    event_name = event_info["EventName"]
    
    included_laps = pd.DataFrame()
    args = plot_args(absolute_compound)
    
    if year == 2021:
        included_laps = df_laps_2021[df_laps_2021.apply(lambda row: lap_filter_round_driver(row, round_number, drivers), axis=1)]
    elif year == 2022:
        included_laps = df_laps_2022[df_laps_2022.apply(lambda row: lap_filter_round_driver(row, round_number, drivers), axis=1)]
    else:
        raise ValueError("Year requested ({}) not available".format(year))
        
    for i in range(len(drivers)):
        row = i // max_width
        col = i % max_width
        
        ax = axes[row][col] if num_row > 1 else axes[col]
        
        driver_color = p.driver_color(drivers[i])
        driver_laps = included_laps[included_laps["Driver"]==drivers[i]]
        
        pit_in_laps = driver_laps[driver_laps["PitInTime"].notnull()]["LapNumber"].to_numpy()
        
        # After pitstops are identified, we can filter for IsAccurate=True and upper_bound
        driver_laps = driver_laps[driver_laps.apply(lambda row: lap_filter_upper_accurate(row, upper_bound), axis=1)]
            
        sns.scatterplot(data=driver_laps, 
                        x="LapNumber", 
                        y=y, 
                        ax=ax, 
                        hue=args[0], 
                        palette=args[1],
                        hue_order=args[3],
                        style="FreshTyre",
                        style_order = [True, False],
                        markers=FreshTyre_markers,
                        legend='auto' if i == num_col-1 else False)
        
        ax.vlines(ymin=plt.yticks()[0][1], ymax=plt.yticks()[0][-2], x=pit_in_laps, label="Pitstop", linestyle="dashed")

        fontdict["color"] = driver_color 
        ax.set_title(label=drivers[i], fontdict=fontdict, fontsize=12)
        
        ax.grid(color=driver_color, which='both', axis='both')
        sns.despine(left=True, bottom=True)
                
    fig.suptitle(t="{} {}".format(year, event_name), fontsize=20)
    axes.flatten()[num_col-1].legend(loc='best', fontsize=8, framealpha=0.5)
    # plt.show()
    
    return fig

# %% [markdown]
# ### Compound Head-to-Head Line Chart

# %%
def lap_filter_round_compound_valid(row, round_number, compounds):
    return row.loc["RoundNumber"] == round_number and row.loc["IsValid"] and row.loc["Compound"] in compounds

# %%
def convert_compound_names(year, round_number, compounds):
    """
    Convert relative compound names to absolute names 
    
    Args:
        compounds: list of str {"SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"}
    
    Returns:
        comp_names: tuple of str {"C1", "C2", "C3", "C4", "C5", "INTERMEDIATE", "WET"}
        
    """
    compound_to_index = {"SOFT":2, "MEDIUM":1, "HARD":0}
    
    return_value = []
    
    for compound in compounds:
        if compound not in slick_tyre_names:
            return_value.append(compound)
        else:
            if year == 2021:
                return_value.append('C' + str(compound_selection_2021[round_number][compound_to_index[compound]]))
            elif year == 2022:
                return_value.append('C' + str(compound_selection_2022[round_number][compound_to_index[compound]]))
    
    return tuple(return_value)


# %%
def plot_compounds_lineplot(years, events, y, x="TyreLife", upper_bound=10, absolute_compound=True, *compounds):
    """
    Plot median values of selected columns for two slick tyre compounds in the selected events to highlight crossover zones
        
    Caveats:
        Only laps with IsValid=True are considered
        
        When absolute_compound=False, different events may use different compounds under the same name 
        e.g. SOFT may be any of C3 to C5 dependinging on the event
    
    Args:
        years: list of int or str
            Championship years of the events
        
        events: list of int or str
            A mix of round numbers or names of the events
            Name is fuzzy matched by fastf1.get_event()
        
        (each (year, event) pair should uniquely identify an event)
        
        *compounds: list of str {"SOFT", "MEDIUM", "HARD"}
            The compounds in the head-to-head
        
        y: str
            The column to use as the y-axis.
            
        x: str {"TyreLife", "LapNumber"} recommended
            The column to use as the x-axis

        upper_bound: float, default: 10
            The upper bound of PctFromFastest for the laps to include
            
            If None, upper bound is set to 30. Use this setting for wet races!
            
            e.g. By default, only laps that are no more than 10% slower than the fastest lap are plotted 
        
        absolute_compound: bool, default: True
            If True, use absolute compound palette (C1, C2 etc.)
            
            If False, use relative compound palette (SOFT, MEDIUM, HARD)
        
    Returns: Figure
    """
    
    assert years and events and len(years) == len(events), "years arg size ({}) does not match events arg size ({})".format(len(years), len(events))
    
    # unpack
    compounds = [compound.upper() for compound in compounds]
    
    for index, compound in enumerate(compounds):
        assert compound in slick_tyre_names, "compound arg {} does not name a slick tyre type".format(compound)
            
    if not absolute_compound:
        print('''
              WARNING: Different events may use different compounds under the same name!
                       e.g. SOFT may be any of C3 to C5 dependinging on the event
              ''')
    
    # Combine years and events and get FastF1 event objects
    event_objects = [f.get_event(years[i], events[i]) for i in range(len(years))]

    plt.style.use("dark_background")
    fig, axes = plt.subplots(nrows=len(event_objects), sharex=True, ncols=1, figsize=(5, 5*len(event_objects)))
    
    # Prevent TypeError when only one event is plotted
    if len(events) == 1:
        axes = [axes]
    
    included_laps_df_list = []
        
    for year, event in zip(years, event_objects):
        df_eligible_laps = pd.DataFrame()
        
        if year == 2021:
            df_eligible_laps = df_laps_2021[df_laps_2021.apply(lambda row: lap_filter_round_compound_valid(row, event["RoundNumber"], compounds), axis=1)]
        elif year == 2022:
            df_eligible_laps = df_laps_2022[df_laps_2022.apply(lambda row: lap_filter_round_compound_valid(row, event["RoundNumber"], compounds), axis=1)]
        else:
            raise ValueError("Year requested ({}) not available".format(year))

        included_laps_df_list.append(df_eligible_laps)
                
    args = plot_args(absolute_compound)
    
    # Copy compounds values
    # May need to convert from relative to absolute names when plotting
    compounds_copy = compounds
 
    for i in range(len(event_objects)):
        included_laps = included_laps_df_list[i]
        medians = included_laps.groupby([args[0], x])[y].median()
        
        if absolute_compound:
            compounds_copy = convert_compound_names(years[i], event_objects[i]["RoundNumber"], compounds)
                            
        for compound in compounds_copy:
            ax = sns.lineplot(x=medians.loc[compound].index, 
                              y=medians.loc[compound].values, 
                              ax=axes[i], 
                              color=args[1][compound],
                              marker=args[2][compound],
                              ms=4,
                              label=compound)

        ax.set_ylabel(y, fontsize=12)
                   
        handles, labels = axes[i].get_legend_handles_labels()
        order = reorder_legend(labels)
        axes[i].legend(handles=[handles[idx] for idx in order], 
                       labels=[labels[idx] for idx in order], 
                       loc="best", 
                       title=args[0],
                       frameon=True,
                       fontsize=10,
                       framealpha=0.5)
        
        ax.set_title(label="{} {}".format(years[i], event_objects[i]["EventName"]), fontsize=12)
        sns.despine(left=True, bottom=True)
                
    # reorder compound names for title
    compounds = [compounds[i] for i in reorder_legend(compounds)]
    
    fig.suptitle(t=" VS ".join(compounds), fontsize="16")
    # plt.show()
    
    return fig

# %% [markdown]
# ### Compound Head-to-Head Boxplot

# %%
def plot_compounds_boxplot(years, events, y, x="TyreLife", upper_bound=10, absolute_compound=True, *compounds):
    """
    Plot median values of selected columns for two slick tyre compounds in the selected events to highlight crossover zones
        
    Caveats:
        Only laps with IsValid=True are considered
        
        When absolute_compound=False, different events may use different compounds under the same name 
        e.g. SOFT may be any of C3 to C5 dependinging on the event
    
    Args:
        years: list of int or str
            Championship years of the events
        
        events: list of int or str
            A mix of round numbers or names of the events
            Name is fuzzy matched by fastf1.get_event()
        
        (each (year, event) pair should uniquely identify an event)
        
        *compounds: list of str {"SOFT", "MEDIUM", "HARD"}
            The compounds in the head-to-head
        
        y: str
            The column to use as the y-axis.
            
        x: str {"TyreLife", "LapNumber"} recommended
            The column to use as the x-axis

        upper_bound: float, default: 10
            The upper bound of PctFromFastest for the laps to include
            
            If None, upper bound is set to 30. Use this setting for wet races!
            
            e.g. By default, only laps that are no more than 10% slower than the fastest lap are plotted 
        
        absolute_compound: bool, default: True
            If True, use absolute compound palette (C1, C2 etc.)
            
            If False, use relative compound palette (SOFT, MEDIUM, HARD)
        
    Returns: Figure
    """
    
    assert years and events and len(years) == len(events), "years arg size ({}) does not match events arg size ({})".format(len(years), len(events))
    
    # unpack
    compounds = [compound.upper() for compound in compounds]
    
    for index, compound in enumerate(compounds):
        assert compound in slick_tyre_names, "compound arg {} does not name a slick tyre type".format(compound)
            
    if not absolute_compound:
        print('''
              WARNING: Different events may use different compounds under the same name!
                       e.g. SOFT may be any of C3 to C5 dependinging on the event
              ''')
    
    # Combine years and events and get FastF1 event objects
    event_objects = [f.get_event(years[i], events[i]) for i in range(len(years))]

    plt.style.use("dark_background")
    fig, axes = plt.subplots(nrows=len(event_objects), sharex=True, ncols=1, figsize=(10, 5*len(event_objects)))
    
    # Prevent TypeError when only one event is plotted
    if len(events) == 1:
        axes = [axes]
    
    included_laps_df_list = []
        
    for year, event in zip(years, event_objects):
        df_eligible_laps = pd.DataFrame()
        
        if year == 2021:
            df_eligible_laps = df_laps_2021[df_laps_2021.apply(lambda row: lap_filter_round_compound_valid(row, event["RoundNumber"], compounds), axis=1)]
        elif year == 2022:
            df_eligible_laps = df_laps_2022[df_laps_2022.apply(lambda row: lap_filter_round_compound_valid(row, event["RoundNumber"], compounds), axis=1)]
        else:
            raise ValueError("Year requested ({}) not available".format(year))

        included_laps_df_list.append(df_eligible_laps)
                
    args = plot_args(absolute_compound)
    
    # Copy compounds values
    # May need to convert from relative to absolute names when plotting
    compounds_copy = compounds
 
    for i in range(len(event_objects)):
        included_laps = included_laps_df_list[i]
        
        if absolute_compound:
            compounds_copy = convert_compound_names(years[i], event_objects[i]["RoundNumber"], compounds)

        ax = sns.boxplot(data=included_laps,
                             x=x,
                             y=y,
                             ax=axes[i],
                             hue=args[0],
                             palette=args[1])

        ax.set_ylabel(y, fontsize=12)
        xticks = ax.get_xticks()
        xticks = [tick+1 for tick in xticks if tick % 5 == 0]
        ax.set_xticks(xticks)
        ax.grid(which='both')
                       
        handles, labels = axes[i].get_legend_handles_labels()
        order = reorder_legend(labels)
        axes[i].legend(handles=[handles[idx] for idx in order], 
                       labels=[labels[idx] for idx in order], 
                       loc="best", 
                       title=args[0],
                       frameon=True,
                       fontsize=10,
                       framealpha=0.5)
        
        ax.set_title(label="{} {}".format(years[i], event_objects[i]["EventName"]), fontsize=12)
        sns.despine(left=True, bottom=True)
    
    # reorder compound names for title
    compounds = [compounds[i] for i in reorder_legend(compounds)]
    
    fig.suptitle(t=" VS ".join(compounds), fontsize="16")
    # plt.show()
    
    return fig

# %% [markdown]
# ## Ad-Hoc

# %%
# df_laps_2022[(df_laps_2022["IsAccurate"]==True) & (df_laps_2022["Driver"].isin(["VER", "PER", "LEC", "SAI", "RUS", "HAM"]))][["EventName", "Driver", "sDeltaToLapRep"]].groupby(["EventName", "Driver"]).mean().to_clipboard()

# %%
# print(mpld3.fig_to_html(plot_driver_lap_times(2022, "Spain", ["VER", "PER", "LEC", "SAI"], "sLapTime")))

# %% [markdown]
# ## Crossover Analysis

# %% [markdown]
# ### Bahrain


