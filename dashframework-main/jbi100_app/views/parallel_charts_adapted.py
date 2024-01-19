# Import libraries
import os

import numpy as np
import pandas as pd

import plotly
import plotly.express as px
import plotly.graph_objs as go

from dash import html, dcc

class ViolinPlots:

    def __init__(self, path : str = "data-used.csv"):
        
        self._read_file(path)
    
    def _read_file(self, path) -> None:
        
        # Read in data
        self.df = pd.read_csv(path, index_col=0)

        print(self.df)

        # read in teams
        self.teams = list(set(self.df['team']))

    def figure(self, features: list[str], teams_to_compare: list[str]) -> plotly.graph_objs.Figure:
        """Returns a parallel coordinates figure of the dataframe filtered for the teams to compare.
        Automatically scales with numer of teams.
        """    
        # split in other countries and selected countries
        df_compare = self.df.loc[self.df["team"].isin(teams_to_compare), features].set_index("team")
        df_others = self.df.loc[~self.df["team"].isin(teams_to_compare), features].drop("team", axis=1)

        # order by mean values (desc)
        df_others = df_others.reindex(df_others.mean().sort_values().index[::-1], axis=1)

        # select colors for teams
        color_compare = ["#f6fa1e", "#f77e05"]

        # select color for others
        color_others = "#433df5"
            
        # add features as violin plots
        fig = go.Figure()

        for idx, feature in enumerate(df_others.columns):
            
            # plot violin plots of the distribution of other teams
            fig.add_trace(go.Violin(x=[feature for x in range(df_others.shape[0])],
                                    y=df_others[feature],
                                    name=feature,
                                    box_visible=True,
                                    meanline_visible=True,
                                    marker_color=color_others,
                                    showlegend=False))
            
            # add markers (for now circles) for teams to compare.
            # Only show the legend for the first circle, otherwise the
            # legend will be repeated for the number of features.
            for color, team in zip(color_compare, teams_to_compare):    
                fig.add_trace(go.Scatter(x=[feature], 
                                        y=[df_compare.loc[team, feature]], 
                                        mode='markers',
                                        name=team,
                                        marker_color=color,
                                        showlegend=(idx == 1)))
                
        return fig