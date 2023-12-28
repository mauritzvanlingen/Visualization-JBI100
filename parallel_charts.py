# Import libraries
import os

import numpy as np
import pandas as pd

import plotly
import plotly.express as px


class ParallelCharts:

    def __init__(self, data_source_path: str = "C:/Users/ljpsm/OneDrive/studie/tue/Visualisation/Assignment/FIFA DataSet/Data/"):
        self.data_source_path = data_source_path

    def _data_path(self, relative: str) -> str:
        return os.path.join(self.data_source_path, relative) 
    
    def read_files(self) -> None:
        # Player data
        self.df_player_defense       = pd.read_csv(self._data_path('FIFA World Cup 2022 Player Data/player_defense.csv'), delimiter=',')
        self.df_player_gca           = pd.read_csv(self._data_path('FIFA World Cup 2022 Player Data/player_gca.csv'), delimiter=',')
        self.df_player_misc          = pd.read_csv(self._data_path('FIFA World Cup 2022 Player Data/player_misc.csv'), delimiter=',')
        self.df_player_passing       = pd.read_csv(self._data_path('FIFA World Cup 2022 Player Data/player_passing.csv'), delimiter=',')
        self.df_player_passing_types = pd.read_csv(self._data_path('FIFA World Cup 2022 Player Data/player_passing_types.csv'), delimiter=',')
        self.df_player_possession    = pd.read_csv(self._data_path('FIFA World Cup 2022 Player Data/player_possession.csv'), delimiter=',')
        self.df_player_shooting      = pd.read_csv(self._data_path('FIFA World Cup 2022 Player Data/player_shooting.csv'), delimiter=',')
        self.df_player_stats         = pd.read_csv(self._data_path('FIFA World Cup 2022 Player Data/player_stats.csv'), delimiter=',')

    def preprocess_data(self):
        self.data_set_main = self._preprocess_main_data()
        self.data_set_stats = self._preprocess_stats_data()
        self.data_set_passes = self._preprocess_passes_data()
        self.data_set_possession = self._preprocess_possession_data()
        self.data_set_shooting = self._preprocess_shooting_data()
        self.data_set_misc = self._preprocess_misc_data()
        self.data_set_defense = self._preprocess_defense_data()

        self.data_sets = ["data_set_main", "data_set_stats", "data_set_passes", "data_set_possession", "data_set_shooting", "data_set_misc", "data_set_defense"]

    def _preprocess_main_data(self) -> pd.DataFrame:
        strong_weak_points = self.df_player_gca[['team', 'player']]
        strong_weak_points['per90'] = self.df_player_gca.apply(lambda x: x['gca_per90'] / x['sca_per90'] if x['sca_per90'] > 0 else 0, axis=1)
        strong_weak_points['passes_live'] = self.df_player_gca.apply(lambda x: x['gca_passes_live'] / x['sca_passes_live'] if x['sca_passes_live'] > 0 else 0, axis=1)
        strong_weak_points['passes_dead'] = self.df_player_gca.apply(lambda x: x['gca_passes_dead'] / x['sca_passes_dead'] if x['sca_passes_dead'] > 0 else 0, axis=1)
        strong_weak_points['dribbles'] = self.df_player_gca.apply(lambda x: x['gca_dribbles'] / x['sca_dribbles'] if x['sca_dribbles'] > 0 else 0, axis=1)
        strong_weak_points['shots'] = self.df_player_gca.apply(lambda x: x['gca_shots'] / x['sca_shots'] if x['sca_shots'] > 0 else 0, axis=1)
        strong_weak_points['fouled'] = self.df_player_gca.apply(lambda x: x['gca_fouled'] / x['sca_fouled'] if x['sca_fouled'] > 0 else 0, axis=1)
        strong_weak_points['defense'] = self.df_player_gca.apply(lambda x: x['gca_defense'] / x['sca_defense'] if x['sca_defense'] > 0 else 0, axis=1)
        strong_weak_points.drop(['player'], axis=1, inplace=True)
        main_chart = strong_weak_points.groupby(by='team').mean()
        main_chart = (main_chart - main_chart.min())/(main_chart.max()-main_chart.min()) # normalize
        main_chart.reset_index(inplace=True)

        return main_chart
    
    def _preprocess_stats_data(self) -> pd.DataFrame:
        stats = self.df_player_stats[['team', 'goals_per90', 'assists_per90', 'xg_per90', 'xg_assist_per90']]
        stats['penality_acc'] = self.df_player_stats.apply(lambda x: x['pens_made'] / x['pens_att'] if x['pens_att'] > 0 else 0, axis=1)
        stats['age'] = self.df_player_stats.apply(lambda x: int(x['age'].split("-")[0]), axis=1)
        stats = stats.groupby(by='team').mean()
        stats = (stats - stats.min())/(stats.max()-stats.min()) # normalize -> also normalize age?
        stats.reset_index(inplace=True)

        return stats
    
    def _preprocess_passes_data(self) -> pd.DataFrame:
        passes_1 = self.df_player_passing[['team', 'assisted_shots', 'passes_into_penalty_area', 'crosses_into_penalty_area']]
        passes_1['passes_completed_pct'] = self.df_player_passing.apply(lambda x: x['passes_completed'] / x['passes'] if x['passes'] > 0 else 0, axis=1)
        passes_1.set_index('team', inplace=True)
        passes_2 = self.df_player_passing_types[['team', 'crosses', 'throw_ins', 'corner_kicks']].set_index('team')
        passes = pd.concat([passes_1, passes_2]).reset_index()
        passes = passes.groupby(by='team').mean()
        passes = (passes - passes.min())/(passes.max()-passes.min()) # normalize -> also normalize age?
        passes.reset_index(inplace=True)

        return passes
    
    def _preprocess_possession_data(self) -> pd.DataFrame:
        possession = self.df_player_possession[['team', 'dribbles_completed_pct']]
        possession['miscontrols_per90'] = self.df_player_possession.apply(lambda x: x['miscontrols'] / x['minutes_90s'] if x['minutes_90s'] > 0 else 0, axis=1)
        possession['dispossessed_per90'] = self.df_player_possession.apply(lambda x: x['dispossessed'] / x['minutes_90s'] if x['minutes_90s'] > 0 else 0, axis=1)
        possession['pct_touches_att_pen_area'] = self.df_player_possession.apply(lambda x: x['touches_att_pen_area'] / x['touches'] if x['touches'] > 0 else 0, axis=1)
        possession['pct_touches_def_pen_area'] = self.df_player_possession.apply(lambda x: x['touches_def_pen_area'] / x['touches'] if x['touches'] > 0 else 0, axis=1)
        possession = possession.groupby(by='team').mean()
        possession = (possession - possession.min())/(possession.max()-possession.min()) # normalize -> also normalize age?
        possession.reset_index(inplace=True)

        return possession
    
    def _preprocess_shooting_data(self) -> pd.DataFrame:
        shooting_1 = self.df_player_shooting[['team', 'shots_on_target_per90', 'shots_on_target_pct', 'average_shot_distance', 'goals_per_shot_on_target', 'shots_free_kicks']].set_index('team')
        shooting_2 = self.df_player_stats[['team', 'goals_per90']].set_index('team')
        shooting = pd.concat([shooting_1, shooting_2]).reset_index()
        shooting = shooting.groupby(by='team').mean()
        shooting = (shooting - shooting.min())/(shooting.max()-shooting.min()) # normalize -> also normalize age?
        shooting.reset_index(inplace=True)

        return shooting
    
    def _preprocess_misc_data(self) -> pd.DataFrame:
        misc = self.df_player_misc[['team', 'cards_yellow', 'cards_yellow_red', 'cards_red', 'offsides']]
        misc['ratio_fouled_to_fouls'] = self.df_player_misc.apply(lambda x: x['fouled'] / x['fouls'] if x['fouls'] > 0 else 0, axis=1)
        misc['ratio_penalties'] = self.df_player_misc.apply(lambda x: x['pens_won'] / x['pens_conceded'] if x['pens_conceded'] > 0 else 0, axis=1)
        misc = misc.groupby(by='team').mean()
        misc = (misc - misc.min())/(misc.max()-misc.min()) # normalize -> also normalize age?
        misc.reset_index(inplace=True)

        return misc
    
    def _preprocess_defense_data(self) -> pd.DataFrame:
        defense_1 = self.df_player_defense[['team', 'blocked_passes', 'clearances', 'errors', 'dribble_tackles_pct', 'blocks', 'interceptions']].set_index('team')
        defense_2 = self.df_player_misc[['team']]
        defense_2['ratio_aerials_won_lost'] = self.df_player_misc.apply(lambda x: x['aerials_won'] / x['aerials_lost'] if x['aerials_lost'] > 0 else 0, axis=1)
        defense_2.set_index('team', inplace=True)
        defense = pd.concat([defense_1, defense_2]).reset_index()
        defense = defense.groupby(by='team').mean()
        defense = (defense - defense.min())/(defense.max()-defense.min()) # normalize -> also normalize age?
        defense.reset_index(inplace=True)

        return defense

    def figure(self, data_set_name: str, *teams_to_compare: list[str]) -> plotly.graph_objs.Figure:
        """Returns a parallel coordinates figure of the dataframe filtered for the teams to compare.
        Automatically scales with numer of teams.
        """
        # check if data set name is in 
        if data_set_name not in self.data_sets:
            raise Exception('Data set not known.')
        
        # filter by countries
        df_filtered = getattr(self, data_set_name).loc[getattr(self, data_set_name)['team'].isin(teams_to_compare)]
        teams = df_filtered["team"].astype('category')
        df_filtered['team'] = teams.cat.codes

        # create color scale
        color_scale = []
        for i in range(len(teams_to_compare)):
            color = 255 * i * 1/len(teams_to_compare)
            color_scale.append((i * (1/len(teams_to_compare)), f"rgb({color}, {color}, {color})"))
            color_scale.append(((i+1) * (1/len(teams_to_compare)), f"rgb({color}, {color}, {color})"))

        # create figure with parallel axis (without the categorial team axis)
        columns = [col for col in df_filtered.columns if col != "team"]
        fig = px.parallel_coordinates(df_filtered, 
                                color='team', 
                                color_continuous_scale=color_scale,
                                dimensions=columns
                                )

        # scale dimensions between 0 and 1
        for dimension in fig.data[0]['dimensions']:
            dimension['range'] = [0, 1]

        # include color bar
        fig.update_layout(coloraxis_colorbar=dict(
            title="Teams",
            tickvals=teams.cat.codes,
            ticktext=teams.cat.categories,
            lenmode="pixels", len=100,
            ))

        return fig