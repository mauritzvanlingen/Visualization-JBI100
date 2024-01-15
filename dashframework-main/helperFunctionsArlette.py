import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


def return_df(list_type):
    df = pd.read_csv(r'C:\Users\20202893\Documents\Data Science & Artficial Intelligence\Y1-Q2\JBI100 - Visualization\FIFA DataSet\Data/FIFA World Cup 2022 Team Data/team_data.csv', delimiter=',')
    if list_type == 'def':
        list_feat = ['gk_free_kick_goals_against', 'gk_corner_kick_goals_against', 'gk_own_goals_against', 'gk_crosses_stopped_pct', 'blocked_shots', 'blocked_passes', 'interceptions', 'clearances', 'errors', 'tackles_def_3rd', 'touches_def_3rd', 'miscontrols', 'dispossessed']
    elif list_type == 'att':
        list_feat = ['shots_on_target_pct', 'goals_per_shot', 'average_shot_distance', 'passes_pct_short', 'passes_pct_medium', 'passes_pct_long', 'tackles_att_3rd', 'touches_att_3rd', 'dribbles', 'passes_received', 'aerials_won_pct', 'passes_offsides']
    elif list_type == 'both':
        list_feat = ['gk_free_kick_goals_against', 'gk_corner_kick_goals_against', 'gk_own_goals_against', 'gk_crosses_stopped_pct', 'blocked_shots', 'blocked_passes', 'interceptions', 'clearances', 'errors', 'tackles_def_3rd', 'touches_def_3rd', 'miscontrols', 'dispossessed', 'shots_on_target_pct', 'goals_per_shot', 'average_shot_distance', 'passes_pct_short', 'passes_pct_medium', 'passes_pct_long', 'tackles_att_3rd', 'touches_att_3rd', 'dribbles', 'passes_received', 'aerials_won_pct', 'passes_offsides']
    return df, list_feat



def list_countries():
    df = pd.read_csv(r'C:\Users\20202893\Documents\Data Science & Artficial Intelligence\Y1-Q2\JBI100 - Visualization\FIFA DataSet\Data\FIFA World Cup 2022 Match Data\data.csv', delimiter=',')
    # Get unique countries from the home_team column
    home_countries = df['home_team'].unique()
    
    # Get unique countries from the away_team column
    away_countries = df['away_team'].unique()
    
    # Combine the arrays and find unique countries from both
    all_countries = pd.unique(pd.concat([pd.Series(home_countries), pd.Series(away_countries)], ignore_index=True))
    
    # Return the unique countries as a list
    return all_countries.tolist()



def most_common_formation(df, country):
    # Filter the DataFrame for matches where the given country is the home team
    home_form = df[df['home_team'] == country]['home_formation']

    # Filter the DataFrame for matches where the given country is the away team
    away_form = df[df['away_team'] == country]['away_formation']

    # Concatenate the home and away formation data
    form_tot = pd.concat([home_form, away_form])

    # Find the most common formation
    most_common = form_tot.value_counts().idxmax()

    return most_common

def formation_to_coordinates(country, field_length=1000, field_width=700):
    df = pd.read_csv(r'C:\Users\20202893\Documents\Data Science & Artficial Intelligence\Y1-Q2\JBI100 - Visualization\FIFA DataSet\Data\FIFA World Cup 2022 Match Data\data.csv', delimiter=',')
    formation = most_common_formation(df, country)
    # Split the formation into parts and convert to integers
    formation_parts = [int(part) for part in formation.split('-')]
    num_lines = len(formation_parts)

    # Calculate the depth of each line on the field
    depths = [field_length * (i+1) / (num_lines+1) for i in range(num_lines)]

    # Define the goalkeeper's position
    positions = [(depths[0] // 2, field_width // 2)]

    # Assign positions for each line
    for line_depth, count in zip(depths, formation_parts):
        # Calculate even spacing for players on the line
        spacing = field_width / (count + 1)
        line_positions = [(line_depth, spacing * (j + 1)) for j in range(count)]
        positions.extend(line_positions)

    return positions

def calculate_normalized_means(stat_type, country):
    # Define the mapping from stat_type to columns
    if stat_type == 'tackles':
        df_global = pd.read_csv(r'C:\Users\20202893\Documents\Data Science & Artficial Intelligence\Y1-Q2\JBI100 - Visualization\FIFA DataSet\Data\FIFA World Cup 2022 Player Data\player_defense.csv', delimiter=',')
    elif stat_type == 'touches':
        df_global = pd.read_csv(r'C:\Users\20202893\Documents\Data Science & Artficial Intelligence\Y1-Q2\JBI100 - Visualization\FIFA DataSet\Data\FIFA World Cup 2022 Player Data\player_possession.csv', delimiter=',')
    df_country = df_global[df_global['team'] == country]
    columns_mapping = {
        'tackles': ['tackles_def_3rd', 'tackles_mid_3rd', 'tackles_att_3rd'],
        'touches': ['touches_def_3rd', 'touches_mid_3rd', 'touches_att_3rd']
    }
    
    # Initialize the list to store normalized means
    normalized_means = []
    
    # Check if the stat_type is recognized and obtain the corresponding columns
    if stat_type in columns_mapping:
        vars = columns_mapping[stat_type]
        # Calculate and store the normalized means
        for var in vars:
            global_mean = df_global[var].dropna().mean()
            country_mean = df_country[var].dropna().mean()
            normalized_means.append((country_mean / global_mean) * 200)
    else:
        raise ValueError("stat_type must be 'tackles' or 'touches'")
    return normalized_means