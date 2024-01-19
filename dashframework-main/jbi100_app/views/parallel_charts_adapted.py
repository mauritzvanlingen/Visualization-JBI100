# Import libraries
import os

import numpy as np
import pandas as pd

import plotly
import plotly.express as px
import plotly.graph_objs as go

from dash import html, dcc

class ViolinPlots:

    def __init__(self,
                 path
                ):
        
        self._read_file(path)

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
    
    def _read_file(self, path : str = "data-used.csv") -> None:
        self.df = pd.read_csv(path, index_col=0)

        # read in teams
        self.teams = list(set(self.df['team']))

    def figure(self, features: list[str], teams_to_compare: list[str]) -> plotly.graph_objs.Figure:
        """Returns a parallel coordinates figure of the dataframe filtered for the teams to compare.
        Automatically scales with numer of teams.
        """    
        # split in other countries and selected countries
        df_compare = self.df.loc[self.df["team"].isin(teams_to_compare)].set_index("team")
        df_others = self.df.loc[~self.df["team"].isin(teams_to_compare)].drop("team", axis=1)

        # order by mean values
        df_others = df_others.reindex(df_others.mean().sort_values().index[::-1], axis=1)

        # select colors for teams
        color_compare = ["#f6fa1e", "#f77e05"]

        # select color for others
        color_others = "#433df5"
            
        # add features as violin plots
        fig = go.Figure()

        for idx, feature in enumerate(df_others.columns):

            fig.add_trace(go.Violin(x=[feature for x in range(df_others.shape[0])],
                                    y=df_others[feature],
                                    name=feature,
                                    box_visible=True,
                                    meanline_visible=True,
                                    marker_color=color_others,
                                    showlegend=False))
            
            for color, team in zip(color_compare, teams_to_compare):    
                fig.add_trace(go.Scatter(x=[feature], 
                                        y=[df_compare.loc[team, feature]], 
                                        mode='markers',
                                        name=team,
                                        marker_color=color,
                                        showlegend=(idx == 1)))
                
        return fig