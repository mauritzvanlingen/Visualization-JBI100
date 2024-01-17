# Import libraries
import os

import numpy as np
import pandas as pd

import plotly
import plotly.express as px

from dash import html, dcc

class ParallelCharts:

    def __init__(self,
                 color_team_1: list[int, int, int],
                 color_team_2: list[int, int, int],
                 data_source_path: str = "C:/Users/ljpsm/OneDrive/studie/tue/Visualisation/Assignment/FIFA DataSet/Data/"):
        self.colors = [color_team_1, color_team_2]
        self.data_source_path = data_source_path

        self.categories = {
            "attack": [
                "shots_on_target_per90", 
                "shots_on_target_pct",
                "goals_per_shot_on_target",
                "into_penalty_area",
                "pct_touches_att_pen_area",
                "xg_per90",
                "average_shot_distance",
                ],
            "defense": [
                "clearances",
                "blocked_passes",
                "blocked_shots",
                "dribble_tackles_pct",
                "tackles_interceptions",
                "errors",
                "miscontrols"
            ],
            "possession": [
                "passes_pct_short",
                "passes_pct_medium",
                "passes_pct_long",
                "passes_total_distance",
                "aerials_won_pct",
                "dispossessed"
            ]
        }

        self.columns = []
        for category_columns in self.categories.values():
            self.columns += category_columns

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
                        
    def preprocess_data(self) -> pd.DataFrame:
        
        # merge all data
        df = pd.concat([
            self.df_player_defense.set_index("team"),
            self.df_player_gca.set_index("team"),
            self.df_player_misc.set_index("team"),
            self.df_player_passing.set_index("team"),
            self.df_player_passing_types.set_index("team"),
            self.df_player_possession.set_index("team"),
            self.df_player_shooting.set_index("team"),
            self.df_player_stats.set_index("team")
        ], axis=1)

        # fill na values
        df.fillna(value = 0, inplace=True)

        # create new variables
        df["into_penalty_area"] = df.apply(lambda x: x["passes_into_penalty_area"] + x["crosses_into_penalty_area"], axis=1)
        df["pct_touches_att_pen_area"] = df.apply(lambda x: x["touches_att_pen_area"] / x["touches"] if x["touches"] > 0 else 0, axis=1)

        # only keep variables that we use
        df = df[self.columns]

        # scale data
        df = (df - df.min())/(df.max()-df.min())

        # take the man per country
        df = df.groupby(by='team').mean()

        # reset index
        self.df = df.reset_index()

        # read in teams
        self.teams = list(set(self.df['team']))

    def figure(self, attributes: list[str], *teams_to_compare: list[str]) -> plotly.graph_objs.Figure:
        """Returns a parallel coordinates figure of the dataframe filtered for the teams to compare.
        Automatically scales with numer of teams.
        """    
        # filter attributes
        df_filtered = self.df[["team", *attributes]]

        # filter by countries
        df_filtered = df_filtered.loc[df_filtered["team"].isin(teams_to_compare)]
        teams = df_filtered["team"].astype('category')
        df_filtered['team'] = teams.cat.codes

        # create color scale
        color_scale = []
        for i in range(2):
            color = f"rgb({self.colors[i][0]}, {self.colors[i][1]}, {self.colors[i][2]})"
            color_scale.append((i * 0.5, color))
            color_scale.append(((i+1) * 0.5, color))

        # create figure with parallel axis (without the categorial team axis)
        columns = [col for col in df_filtered.columns if col != "team"]
        fig = px.parallel_coordinates(
            df_filtered, 
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
        
        return dcc.Graph(
            id=f'parallel',
            figure=fig
            )
            
    def menu_layout(self):

        description_card = html.Div(
        id="description-card",
        children=[
            html.H5("Player data"),
            html.Div(
                id="intro",
                children="Choose the teams to compare and the graphs to view.",
                ),
            ],
        )

        # Selecting teams
        team_card = html.Div(
        id="team-card",
        children=[
            html.Label("Team 1"),
            dcc.Dropdown(
                id="select-team-1",
                options=[{"label": i, "value": i} for i in self.teams],
                value=self.teams[0],
            ),
            html.Br(),
            html.Label("Team 2"),
            dcc.Dropdown(
                id="select-team-2",
                options=[{"label": i, "value": i} for i in self.teams],
                value=self.teams[1],
                ),
            html.Br(),
            ], style={"textAlign": "float-left"}
        )

        # Label for graphs of Interest
        graph_card = html.Div(
        id="feature-card",
        children=[
            html.Label("Features to add"),
                # Dropdown for selecting graphs
                dcc.Dropdown(
                    id='graph-dropdown',
                    multi=True,
                    options=self.columns,
                ),
            html.Br(),
            ], style={"textAlign": "float-left"}
        )

        # # Explanation of columns
        # explanation_card = html.Div(
        # id="explanation-card",
        # children=[
        #     html.Label("Explanation of variables"),
        #     dcc.Dropdown(
        #         id="explanation_selection",
        #         value=[],
        #         options=self.get_variables(self.data_sets[0])
        #     ),
        #     html.Br(),
        #     html.Div(
        #         id="explanation",
        #         children="Choose a variable for which to show the explanation here.",
        #         ),
        #     ], style={"textAlign": "float-left"}
        # )
        
        return [description_card, team_card, graph_card]