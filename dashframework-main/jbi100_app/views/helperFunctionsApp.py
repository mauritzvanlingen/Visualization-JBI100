import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm

def get_cats():
    """
    Extracts and organizes the categories of player data (attack, possession, defense)
    from CSV files. Returns a dictionary with categories as keys and lists of feature
    names as values.

    Returns:
        dict: A dictionary containing the categories and their corresponding features.
    """
   # Read CSV files containing player data
    df_player_gca = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/player_gca.csv', delimiter=',')
    df_player_possession = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/player_possession.csv', delimiter=',')
    df_player_defense = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/player_defense.csv', delimiter=',')

    # Extract column names from the dataframes
    col1 = list(df_player_gca.columns)
    col2 = list(df_player_possession.columns)
    col3 = list(df_player_defense.columns)
    cols = [col1, col2, col3]

    # Define columns to be removed
    remove_rows = ['player', 'position', 'age', 'birth_year', 'minutes_90s']
    
    # Remove specified columns and add 'minutes' to each category
    for col in cols:
        col.append('minutes')
        for item in remove_rows:
            while item in col:
                col.remove(item)
    
    # Organize features into categories
    features = {'attack': col1, 'possession': col2, 'defense': col3}
    return features
    

def create_merged_df(features):
    """
    Creates a merged DataFrame by reading team data and FIFA ranking data from CSV files,
    then merging them based on the team name. The data is normalized based on the number
    of matches played.

    Args:
        features (list): List of features to include in the merged DataFrame.

    Returns:
        pd.DataFrame: A normalized DataFrame containing merged team and FIFA ranking data.
    """    
    # Read team data and FIFA ranking data from CSV files
    df_team = pd.read_csv("../Data/FIFA World Cup 2022 Team Data/team_data.csv")
    df_fifa = pd.read_csv("../Data/FIFA World Cup Historic/fifa_ranking_2022-10-06.csv")

    # Reduce team DataFrame to selected features
    df_red = df_team[features]

    # Merge team data with FIFA ranking data
    merged_df = pd.merge(df_red, df_fifa[['team', 'rank', 'points']], on='team')
    red_mer_df = merged_df.set_index('team')

    # Normalize data based on the number of matches played
    norm_df = red_mer_df.copy()
    norm_df['nr_match'] = norm_df['minutes'] / 90
    norm_df = norm_df.apply(lambda row: row / row['nr_match'], axis=1)
    
    # Keep certain columns unnormalized
    norm_df[['minutes', 'rank', 'dribble_tackles_pct', 'dribbles_completed_pct', 'gca_per90', 'sca_per90', 'points']] = red_mer_df[['minutes', 'rank', 'dribble_tackles_pct', 'dribbles_completed_pct', 'gca_per90', 'sca_per90', 'points']]
    return norm_df

def corr_plots(cat_key, cats, df, selected_countries):
    """
    Generates a series of scatter plots showing the correlation between selected features
    and FIFA points. Each subplot represents the correlation for one feature.

    Args:
        cat_key (str): The key representing the category of features (e.g., 'attack', 'defense').
        cats (dict): Dictionary containing categories and their corresponding features.
        df (pd.DataFrame): The DataFrame containing the data to be used in the plots.

    Returns:
        go.Figure: A Plotly graph object figure containing the subplots.
    """
    # Select features based on the category key
    selected_features = cats[cat_key]

    # Define rows to be removed from the analysis
    remove_rows = ['rank', 'points', 'team', 'minutes']

    # Remove specified rows from the selected features
    for item in remove_rows:
        while item in selected_features:
            selected_features.remove(item)

    # Create subplot titles
    subplot_titles = [f"{feature} vs FIFA Points" for feature in selected_features if feature != 'points']
    num_plots = len(subplot_titles)

    # Create a figure with subplots
    fig = make_subplots(rows=num_plots, cols=1, subplot_titles=subplot_titles)

    cmap = plt.get_cmap('hsv', 13)
    colors = cmap(np.linspace(0, 1, 13))
    hex_colors = [cm.colors.rgb2hex(color) for color in colors]
    country_colors = {country: hex_colors[i] for i, country in enumerate(selected_countries)}
    

    # Add scatter plots to the figure
    for i, feature in enumerate(selected_features, 1):
        
        data_red = df[[feature, 'points']]
        point_colors = ['grey' if team not in selected_countries else country_colors[team] for team in df['team']]
        
        correlation = data_red.corr().iloc[0, 1]
        subplot_title = f"{feature} vs FIFA Points (Correlation: {correlation:.2f})"
        fig.add_trace(go.Scatter(x=data_red[feature], y=data_red['points'], mode='markers', name=feature, showlegend=False, text=df['team'],
                                 selected=dict(marker=dict(color='blue')), marker_color=point_colors), row=i, col=1,
                      )
        fig['layout']['annotations'][i-1]['text'] = subplot_title
        fig.update_xaxes(title_text=feature, row=i, col=1)
        fig.update_yaxes(title_text="FIFA Points", row=i, col=1)
        fig.update_layout(clickmode='event+select')

    # Update layout of the figure
    fig.update_layout(height=300 * num_plots, width=800, title='Click point to include feature or select (max. 12) to include countries')
    return fig


def get_descriptions(feature):
    """
    Provides descriptions for various features used in the analysis.
    
    Args:
        feature (str): The name of the feature for which the description is requested.
    
    Returns:
        str: A description of the specified feature.
    """
    descriptions = {"players_used": "Number of Players used in Games",
  "avg_age": "Age is weighted by minutes played",
  "possession": " Possession  Calculated as the percentage of passes attempted",
  "games": "Matches Played by the player or squad",
  "games_starts": "Game or games started by player",
  "minutes_90s": " 90s played  Minutes played divided by 90",
  "goals": "Goals scored or allowed",
  "assists": "Assists",
  "goals_pens": "Non-Penalty Goals",
  "pens_made": "Penalty Kicks Made",
  "pens_att": "Penalty Kicks Attempted",
  "cards_yellow": "Yellow Cards",
  "cards_red": "Red Cards",
  "goals_per90": "Goals Scored per 90 minutes Minimum 30 minutes played per squad game to qualify as a leader",
  "assists_per90": "Assists per 90 minutes Minimum 30 minutes played per squad game to qualify as a leader",
  "goals_assists_per90": "Goals and Assists per 90 minutes Minimum 30 minutes played per squad game to qualify as a leader",
  "goals_pens_per90": "Goals minus Penalty Kicks made per 90 minutes Minimum 30 minutes played per squad game to qualify as a leader",
  "goals_assists_pens_per90": "Goals plus Assists minus Penalty Kicks made per 90 minutes Minimum 30 minutes played per squad game to qualify as a leader",
  "xg": "Expected Goals xG totals include penalty kicks, but do not include penalty shootouts (unless otherwise noted). Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available.",
  "npxg": " Non-Penalty Expected Goals  Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available.",
  "xg_assist": " Expected Assisted Goals  xG which follows a pass that assists a shot Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available.",
  "npxg_xg_assist": "Non-Penalty Expected Goals plus Assisted Goals xG totals include penalty kicks, but do not include penalty shootouts (unless otherwise noted). Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available. Minimum 30 minutes played per squad game to qualify as a leader",
  "xg_per90": "Expected Goals per 90 minutes xG totals include penalty kicks, but do not include penalty shootouts (unless otherwise noted). Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available. Minimum 30 minutes played per squad game to qualify as a leader",
  "xg_assist_per90": "Expected Assisted Goals per 90 minutes Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available. Minimum 30 minutes played per squad game to qualify as a leader",
  "xg_xg_assist_per90": "Expected Goals plus Assisted Goals per 90 minutes xG totals include penalty kicks, but do not include penalty shootouts (unless otherwise noted). Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available. Minimum 30 minutes played per squad game to qualify as a leader",
  "npxg_per90": "Non-Penalty Expected Goals per 90 minutes Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available. Minimum 30 minutes played per squad game to qualify as a leader",
  "npxg_xg_assist_per90": "Non-Penalty Expected Goals plus Assisted Goals per 90 minutes Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available. Minimum 30 minutes played per squad game to qualify as a leader",
  "gk_games": "Matches Played by the player or squad",
  "gk_games_starts": "Game or games started by player",
  "gk_goals_against": "Goals Against",
  "gk_goals_against_per90": "Goals Against per 90 minutes",
  "gk_shots_on_target_against": "Shots on Target Against",
  "gk_save_pct": "Save Percentage (Shots on Target Against - Goals Against)/Shots on Target Against Note that not all shots on target are stopped by the keeper, many will be stopped by defenders Does not include penalty kicks",
  "gk_wins": "Wins",
  "gk_ties": "Draws",
  "gk_losses": "Losses",
  "gk_clean_sheets": "Clean Sheets Full matches by goalkeeper where no goals are allowed.",
  "gk_clean_sheets_pct": "Clean Sheet Percentage Percentage of matches that result in clean sheets.",
  "gk_pens_att": "Penalty Kicks Attempted",
  "gk_pens_allowed": "Penalty Kicks Allowed",
  "gk_pens_saved": "Penalty Kicks Saved",
  "gk_pens_missed": "Penalty Kicks Missed",
  "gk_pens_save_pct": "Penalty Save Percentage Penalty Kick Goals Against/Penalty Kick Attempts Penalty shots that miss the target are not included",
  "gk_free_kick_goals_against": "Free Kick Goals Against",
  "gk_corner_kick_goals_against": "Corner Kick Goals Against",
  "gk_own_goals_against": "Own Goals Scored Against Goalkeeper",
  "gk_psxg": "Post-Shot Expected Goals PSxG is expected goals based on how likely the goalkeeper is to save the shot xG totals include penalty kicks, but do not include penalty shootouts (unless otherwise noted). Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available.",
  "gk_psnpxg_per_shot_on_target_against": "Post-Shot Expected Goals per Shot on Target Not including penalty kicks PSxG is expected goals based on how likely the goalkeeper is to save the shot Higher numbers indicate that shots on target faced are more difficult to stop and more likely to score An underline indicates there is a match that is missing data, but will be updated when available.",
  "gk_psxg_net": "Post-Shot Expected Goals minus Goals Allowed Positive numbers suggest better luck or an above average ability to stop shots PSxG is expected goals based on how likely the goalkeeper is to save the shot Note: Does not include own goals xG totals include penalty kicks, but do not include penalty shootouts (unless otherwise noted). Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available.",
  "gk_psxg_net_per90": "Post-Shot Expected Goals minus Goals Allowed per 90 minutes Positive numbers suggest better luck or an above average ability to stop shots PSxG is expected goals based on how likely the goalkeeper is to save the shot Note: Does not include own goals xG totals include penalty kicks, but do not include penalty shootouts (unless otherwise noted). Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available.",
  "gk_passes_completed_launched": " Passes Completed  Passes longer than 40 yards",
  "gk_passes_launched": " Passes Attempted  Passes longer than 40 yards",
  "gk_passes_pct_launched": " Pass Completion Percentage  Passes longer than 40 yards",
  "gk_passes": "Passes Attempted Not including goal kicks",
  "gk_passes_throws": "Throws Attempted",
  "gk_pct_passes_launched": " Percentage of Passes that were Launched  Not including goal kicks Passes longer than 40 yards",
  "gk_passes_length_avg": "Average length of passes, in yards Not including goal kicks",
  "gk_goal_kicks": "Goal Kicks Attempted",
  "gk_pct_goal_kicks_launched": " Percentage of Goal Kicks that were Launched  Passes longer than 40 yards",
  "gk_goal_kick_length_avg": "Average length of goal kicks, in yards",
  "gk_crosses": "Opponent's attempted crosses into penalty area",
  "gk_crosses_stopped": "Number of crosses into penalty area which were successfully stopped by the goalkeeper",
  "gk_crosses_stopped_pct": "Percentage of crosses into penalty area which were successfully stopped by the goalkeeper",
  "gk_def_actions_outside_pen_area": "# of defensive actions outside of penalty area",
  "gk_def_actions_outside_pen_area_per90": "Defensive actions outside of penalty area per 90 minutes",
  "gk_avg_distance_def_actions": "Average distance from goal (in yards) of all defensive actions",
  "shots": "Shots Total Does not include penalty kicks",
  "shots_on_target": "Shots on target Note: Shots on target do not include penalty kicks",
  "shots_on_target_pct": "Percentage of shots that are on target Minimum .395 shots per squad game to qualify as a leader Note: Shots on target do not include penalty kicks",
  "shots_per90": "Shots total per 90 minutes Minimum 30 minutes played per squad game to qualify as a leader",
  "shots_on_target_per90": "Shots on target per 90 minutes Minimum 30 minutes played per squad game to qualify as a leader Note: Shots on target do not include penalty kicks",
  "goals_per_shot": "Goals per shot Minimum .395 shots per squad game to qualify as a leader",
  "goals_per_shot_on_target": "Goals per shot on target Minimum .111 shots on target per squad game to qualify as a leader Note: Shots on target do not include penalty kicks",
  "average_shot_distance": "Average distance, in yards, from goal of all shots taken Minimum .395 shots per squad game to qualify as a leader Does not include penalty kicks",
  "shots_free_kicks": "Shots from free kicks",
  "npxg_per_shot": "Non-Penalty Expected Goals per shot Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available. Minimum .395 shots per squad game to qualify as a leader",
  "xg_net": " Goals minus Expected Goals  xG totals include penalty kicks, but do not include penalty shootouts (unless otherwise noted). Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available.",
  "npxg_net": " Non-Penalty Goals minus Non-Penalty Expected Goals  xG totals include penalty kicks, but do not include penalty shootouts (unless otherwise noted). Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available.",
  "passes_completed": "Passes Completed",
  "passes": "Passes Attempted",
  "passes_pct": "Pass Completion Percentage Minimum 30 minutes played per squad game to qualify as a leader",
  "passes_total_distance": "Total distance, in yards, that completed passes have traveled in any direction",
  "passes_progressive_distance": "Progressive Distance Total distance, in yards, that completed passes have traveled towards the opponent's goal. Note: Passes away from opponent's goal are counted as zero progressive yards.",
  "passes_completed_short": "Passes Completed Passes between 5 and 15 yards",
  "passes_short": "Passes Attempted Passes between 5 and 15 yards",
  "passes_pct_short": "Pass Completion Percentage Passes between 5 and 15 yards Minimum 30 minutes played per squad game to qualify as a leader",
  "passes_completed_medium": "Passes Completed Passes between 15 and 30 yards",
  "passes_medium": "Passes Attempted Passes between 15 and 30 yards",
  "passes_pct_medium": "Pass Completion Percentage Passes between 15 and 30 yards Minimum 30 minutes played per squad game to qualify as a leader",
  "passes_completed_long": "Passes Completed Passes longer than 30 yards",
  "passes_long": "Passes Attempted Passes longer than 30 yards",
  "passes_pct_long": "Pass Completion Percentage Passes longer than 30 yards Minimum 30 minutes played per squad game to qualify as a leader",
  "pass_xa": " Expected Assists  The likelihood each completed pass becomes a goal assists given the pass type, phase of play, location and distance. Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available. Minimum 30 minutes played per squad game to qualify as a leader",
  "xg_assist_net": " Assists minus Expected Goals Assisted  Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available.",
  "assisted_shots": "Passes that directly lead to a shot (assisted shots)",
  "passes_into_final_third": "Completed passes that enter the 1/3 of the pitch closest to the goal Not including set pieces",
  "passes_into_penalty_area": "Completed passes into the 18-yard box Not including set pieces",
  "crosses_into_penalty_area": "Completed crosses into the 18-yard box Not including set pieces",
  "progressive_passes": "Progressive Passes Completed passes that move the ball towards the opponent's goal at least 10 yards from its furthest point in the last six passes, or any completed pass into the penalty area. Excludes passes from the defending 40% of the pitch",
  "passes_live": "Live-ball passes",
  "passes_dead": "Dead-ball passes Includes free kicks, corner kicks, kick offs, throw-ins and goal kicks",
  "passes_free_kicks": "Passes attempted from free kicks",
  "through_balls": "Completed pass sent between back defenders into open space",
  "passes_switches": "Passes that travel more than 40 yards of the width of the pitch",
  "crosses": "Crosses",
  "throw_ins": "Throw-Ins taken",
  "corner_kicks": "Corner Kicks",
  "corner_kicks_in": "Inswinging Corner Kicks",
  "corner_kicks_out": "Outswinging Corner Kicks",
  "corner_kicks_straight": "Straight Corner Kicks",
  "passes_offsides": "Offsides",
  "passes_blocked": "Blocked by the opponent who was standing it the path",
  "sca": "Shot-Creating Actions The two offensive actions directly leading to a shot, such as passes, dribbles and drawing fouls. Note: A single player can receive credit for multiple actions and the shot-taker can also receive credit.",
  "sca_per90": "Shot-Creating Actions per 90 minutes Minimum 30 minutes played per squad game to qualify as a leader",
  "sca_passes_live": "Completed live-ball passes that lead to a shot attempt",
  "sca_passes_dead": "Completed dead-ball passes that lead to a shot attempt. Includes free kicks, corner kicks, kick offs, throw-ins and goal kicks",
  "sca_dribbles": "Successful dribbles that lead to a shot attempt",
  "sca_shots": "Shots that lead to another shot attempt",
  "sca_fouled": "Fouls drawn that lead to a shot attempt",
  "sca_defense": "Defensive actions that lead to a shot attempt",
  "gca": "Goal-Creating Actions The two offensive actions directly leading to a goal, such as passes, dribbles and drawing fouls. Note: A single player can receive credit for multiple actions and the shot-taker can also receive credit.",
  "gca_per90": "Goal-Creating Actions per 90 minutes Minimum 30 minutes played per squad game to qualify as a leader",
  "gca_passes_live": "Completed live-ball passes that lead to a goal",
  "gca_passes_dead": "Completed dead-ball passes that lead to a goal. Includes free kicks, corner kicks, kick offs, throw-ins and goal kicks",
  "gca_dribbles": "Successful dribbles that lead to a goal",
  "gca_shots": "Shots that lead to another goal-scoring shot",
  "gca_fouled": "Fouls drawn that lead to a goal",
  "gca_defense": "Defensive actions that lead to a goal",
  "tackles": "Number of players tackled",
  "tackles_won": "Tackles in which the tackler's team won possession of the ball",
  "tackles_def_3rd": "Tackles in defensive 1/3",
  "tackles_mid_3rd": "Tackles in middle 1/3",
  "tackles_att_3rd": "Tackles in attacking 1/3",
  "dribble_tackles": "Number of dribblers tackled",
  "dribbles_vs": "Number of times dribbled past plus number of tackles",
  "dribble_tackles_pct": " Percentage of dribblers tackled  Dribblers tackled divided by dribblers tackled plus times dribbled past Minimum .625 dribblers contested per squad game to qualify as a leader",
  "dribbled_past": "Number of times dribbled past by an opposing player",
  "blocks": "Number of times blocking the ball by standing in its path",
  "blocked_shots": "Number of times blocking a shot by standing in its path",
  "blocked_passes": "Number of times blocking a pass by standing in its path",
  "interceptions": "Interceptions",
  "tackles_interceptions": "Number of players tackled plus number of interceptions",
  "clearances": "Clearances",
  "errors": "Mistakes leading to an opponent's shot",
  "touches": "Number of times a player touched the ball. Note: Receiving a pass, then dribbling, then sending a pass counts as one touch",
  "touches_def_pen_area": "Touches in defensive penalty area",
  "touches_def_3rd": "Touches in defensive 1/3",
  "touches_mid_3rd": "Touches in middle 1/3",
  "touches_att_3rd": "Touches in attacking 1/3",
  "touches_att_pen_area": "Touches in attacking penalty area",
  "touches_live_ball": "Live-ball touches. Does not include corner kicks, free kicks, throw-ins, kick-offs, goal kicks or penalty kicks",
  "dribbles_completed": "Dribbles Completed Successfully",
  "dribbles": "Dribbles Attempted",
  "dribbles_completed_pct": "Percentage of Dribbles Completed Successfully Minimum .5 dribbles per squad game to qualify as a leader",
  "miscontrols": "Number of times a player failed when attempting to gain control of a ball",
  "dispossessed": "Number of times a player loses control of the ball after being tackled by an opposing player. Does not include attempted dribbles",
  "passes_received": "Number of times a player successfully received a pass",
  "progressive_passes_received": "Progressive Passes Received Completed passes that move the ball towards the opponent's goal at least 10 yards from its furthest point in the last six passes, or any completed pass into the penalty area. Excludes passes from the defending 40% of the pitch",
  "minutes_per_game": "Minutes Per Match Played",
  "minutes_pct": " Percentage of Minutes Played  Percentage of team's total minutes in which player was on the pitch Player minutes played divided by team total minutes played Minimum 30 minutes played per squad game to qualify as a leader",
  "minutes_per_start": "Minutes Per Match Started Minimum 30 minutes played per squad game to qualify as a leader",
  "games_complete": "Complete matches played",
  "games_subs": "Games as sub Game or games player did not start, so as a substitute",
  "minutes_per_sub": "Minutes Per Substitution Minimum 30 minutes played per squad game to qualify as a leader",
  "unused_subs": "Games as an unused substitute",
  "points_per_game": " Points per Match  Average number of points earned by the team from matches in which the player appeared Minimum 30 minutes played per squad game to qualify as a leader",
  "on_goals_for": "Goals scored by team while on pitch",
  "on_goals_against": "Goals allowed by team while on pitch",
  "plus_minus": " Plus/Minus  Goals scored minus goals allowed by the team while the player was on the pitch.",
  "plus_minus_per90": " Plus/Minus per 90 Minutes  Goals scored minus goals allowed by the team while the player was on the pitch per 90 minutes played. Minimum 30 minutes played per squad game to qualify as a leader",
  "on_xg_for": "Expected goals by team while on pitch xG totals include penalty kicks, but do not include penalty shootouts (unless otherwise noted). Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available.",
  "on_xg_against": "Expected goals allowed by team while on pitch xG totals include penalty kicks, but do not include penalty shootouts (unless otherwise noted). Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available.",
  "xg_plus_minus": " xG Plus/Minus  Expected goals scored minus expected goals allowed by the team while the player was on the pitch. xG totals include penalty kicks, but do not include penalty shootouts (unless otherwise noted). Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available.",
  "xg_plus_minus_per90": " xG Plus/Minus per 90 Minutes  Expected goals scored minus expected goals allowed by the team while the player was on the pitch per 90 minutes played. xG totals include penalty kicks, but do not include penalty shootouts (unless otherwise noted). Provided by Opta. An underline indicates there is a match that is missing data, but will be updated when available. Minimum 30 minutes played per squad game to qualify as a leader",
  "cards_yellow_red": "Second Yellow Card",
  "fouls": "Fouls Committed",
  "fouled": "Fouls Drawn",
  "offsides": "Offsides",
  "pens_won": "Penalty Kicks Won",
  "pens_conceded": "Penalty Kicks Conceded",
  "own_goals": "Own Goals",
  "ball_recoveries": "Number of loose balls recovered",
  "aerials_won": "Aerials won",
  "aerials_lost": "Aerials lost",
  "aerials_won_pct": "Percentage of aerials won Minimum .97 aerial duels per squad game to qualify as a leader"}
    return descriptions[feature]

def get_labels(feature):
  """
    Provides user-friendly labels for various features used in the analysis.
    
    Args:
        feature (str): The name of the feature for which the label is requested.
    
    Returns:
        str: A user-friendly label for the specified feature.
    """
  labels = {
    'tackles': 'Tackles',
    'blocks': 'Blocks',
    'interceptions': 'Interceptions',
    'clearances': 'Clearances',
    'errors': 'Errors',
    'team': 'Team',
    'minutes': 'Minutes',
    'tackles_won': 'Tackles won',
    'tackles_def_3rd': 'Tackles in def',
    'tackles_mid_3rd': 'Tackles in mid',
    'tackles_att_3rd': 'Tackles in att',
    'dribble_tackles': 'Dribblers tackled',
    'dribbles_vs': 'Dribbled and tackles',
    'dribble_tackles_pct': 'Percentage dribblers tackled',
    'dribbled_past': 'Dribbled past',
    'blocked_shots': 'Blocking shots',
    'blocked_passes': 'Blocking passes',
    'tackles_interceptions': 'Tackles and interceptions',
    'touches': 'Touches',
    'touches_def_pen_area': 'Touches def penalty area',
    'touches_def_3rd': 'Touches in def',
    'touches_mid_3rd': 'Touches in mid',
    'touches_att_3rd': 'Touches in att',
    'touches_att_pen_area': 'Touches in att penalty area',
    'touches_live_ball': 'Live-ball touches',
    'dribbles_completed': 'Dribbles completed',
    'dribbles': 'Dribbles attempted',
    'dribbles_completed_pct': 'Percentage dribbles completed',
    'miscontrols': 'Failed control attempt',
    'dispossessed': 'Lost control',
    'passes_received': 'Passes received',
    'progressive_passes_received': 'Progressive passes received',
    'sca_per90': 'SCA per 90',
    'sca_passes_live': 'SCA completed live',
    'sca_passes_dead': 'SCA completed dead',
    'sca_dribbles': 'SCA dribbles',
    'sca_shots': 'SCA shots',
    'sca_fouled': 'SCA fouls',
    'sca_defense': 'SCA defensive',
    'gca_per90': 'GCA per 90',
    'sca': 'Shot-Creating Actions',
    'gca': 'Goal-Creating Actions',
    'gca_passes_live': 'GCA completed live',
    'gca_passes_dead': 'GCA completed dead',
    'gca_dribbles': 'GCA dribbles',
    'gca_shots': 'GCA shots',
    'gca_fouled': 'GCA fouls',
    'gca_defense': 'GCA defensive',
    'points': 'Total points in FIFA ranking'}

  return labels[feature]

def getFeatFromLabel(label):
  """
    Provides the feature name corresponding to a given user-friendly label.
    
    Args:
        label (str): The user-friendly label of the feature.
    
    Returns:
        str: The name of the feature corresponding to the given label.
  """
  labels = {
    'tackles': 'Tackles',
    'blocks': 'Blocks',
    'interceptions': 'Interceptions',
    'clearances': 'Clearances',
    'errors': 'Errors',
    'team': 'Team',
    'minutes': 'Minutes',
    'tackles_won': 'Tackles won',
    'tackles_def_3rd': 'Tackles in def',
    'tackles_mid_3rd': 'Tackles in mid',
    'tackles_att_3rd': 'Tackles in att',
    'dribble_tackles': 'Dribblers tackled',
    'dribbles_vs': 'Dribbled and tackles',
    'dribble_tackles_pct': 'Percentage dribblers tackled',
    'dribbled_past': 'Dribbled past',
    'blocked_shots': 'Blocking shots',
    'blocked_passes': 'Blocking passes',
    'tackles_interceptions': 'Tackles and interceptions',
    'touches': 'Touches',
      'touches_def_pen_area': 'Touches def penalty area',
      'touches_def_3rd': 'Touches in def',
      'touches_mid_3rd': 'Touches in mid',
      'touches_att_3rd': 'Touches in att',
      'touches_att_pen_area': 'Touches in att penalty area',
      'touches_live_ball': 'Live-ball touches',
      'dribbles_completed': 'Dribbles completed',
      'dribbles': 'Dribbles attempted',
      'dribbles_completed_pct': 'Percentage dribbles completed',
      'miscontrols': 'Failed control attempt',
      'dispossessed': 'Lost control',
      'passes_received': 'Passes received',
      'progressive_passes_received': 'Progressive passes received',
      'sca_per90': 'SCA per 90',
      'sca_passes_live': 'SCA completed live',
      'sca_passes_dead': 'SCA completed dead',
      'sca_dribbles': 'SCA dribbles',
      'sca_shots': 'SCA shots',
      'sca_fouled': 'SCA fouls',
      'sca_defense': 'SCA defensive',
      'gca_per90': 'GCA per 90',
      'sca': 'Shot-Creating Actions',
      'gca': 'Goal-Creating Actions',
      'gca_passes_live': 'GCA completed live',
      'gca_passes_dead': 'GCA completed dead',
      'gca_dribbles': 'GCA dribbles',
      'gca_shots': 'GCA shots',
      'gca_fouled': 'GCA fouls',
      'gca_defense': 'GCA defensive'}
  for key, val in labels.items():
    if val == label:
        return key




