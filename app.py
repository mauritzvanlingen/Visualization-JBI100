from jbi100_app.main import app
from jbi100_app.views.menu import make_menu_layout
from jbi100_app.views.scatterplot import Scatterplot

from dash import html, dcc
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go

if __name__ == '__main__':
    # Load data
    df_player_keepersadv = pd.read_csv(r"C:\Users\Beheerder\Documents\DSAI master\Q2 Courses\Vizualisation\dashframework-main\dashframework-main\FIFA DataSet\FIFA DataSet\Data\FIFA World Cup 2022 Player Data\player_keepersadv.csv", delimiter=',') #change path to your own for now
    numerical_columns = df_player_keepersadv.select_dtypes(include=['number']).columns

    
    def convert_age(age_str):
        years, days = map(int, age_str.split('-'))
        # Assuming 365.25 days per year to account for leap years
        fraction_of_year = days / 365.25
        return years + fraction_of_year

    # Apply the conversion to the 'age' column
    df_player_keepersadv['age'] = df_player_keepersadv['age'].apply(convert_age)
    
    #standardize all numerical data
    df_player_keepersadv[numerical_columns] = df_player_keepersadv[numerical_columns].apply(lambda x: x / x.max())
    #give the columns neater names (still a tad long)
    df_player_keepersadv.rename(columns={'birth_year': 'Birth Year', 
                                         'minutes_90s': 'Minutes per 90 min',
                                         "gk_goals_agains":"Goals Against",
                                         "gk_pens_allowed": "Penalties Kicks Allowed",
                                         "gk_free_kick_goals_against": "Free Kick Goal Against",
                                         "gk_corner_kick_goals_against": "Corner Kick Goals Against",
                                         "gk_own_goals_against": "Own Goals by Goalkeeper",
                                         "gk_psxg": "Post-Shot Expected Goals",
                                         "gk_psnpxg_per_shot_on_target_against": "Post-Shot Expected Goals per Shot on Target Not including penalty kicks", 
                                         "gk_psxg_net": "Post-Shot Expected Goals minus Goals Allowed",
                                         "gk_psxg_net_per90":"Post-Shot Expected Goals minus Goals Allowed per 90 minutes",
                                         "gk_passes_completed_launched":"Passes Completed Passes longer than 40 yards",
                                         "gk_passes_launched":"Passes Attempted Passes longer than 40 yards",
                                         "gk_passes_pct_launched": "Pass Completion Percentage Passes longer than 40 yards",
                                         "gk_passes": "Passes Attempted Not including goal kicks",
                                         "gk_passes_throws": "Throws Attempted",
                                         "gk_pct_passes_launched":" Percentage of Passes that were Launched Not including goal kicks Passes longer than 40 yards",
                                         "gk_passes_length_avg":"Average length of passes",
                                         "gk_goal_kicks": "Goal Kicks Attempted" ,
                                         "gk_pct_goal_kicks_launched":" Percentage of Goal Kicks that were Launched Passes longer than 40 yards",
                                         "gk_goal_kick_length_avg":"Average length of goal kicks (yards)",
                                         "gk_crosses": "Opponent's attempted crosses into penalty area",
                                         "gk_crosses_stopped":"Number of crosses into penalty area stopped by the goalkeeper",
                                         "gk_crosses_stopped_pct": "Percentage of crosses into penalty area stopped by the goalkeeper",
                                         "gk_def_actions_outside_pen_area": "Number of defensive actions outside of penalty area",
                                         "gk_def_actions_outside_pen_area_per90":"Defensive actions outside of penalty area per 90 minutes",
                                         "gk_avg_distance_def_actions": "Average distance from goal (in yards) of all defensive actions", 
                                         
                                         }, inplace=True)

    # Instantiate custom views
    scatterplot_view = Scatterplot("Scatterplot 1", 'goals against', 'minutes 90s', df_player_keepersadv)

    # App layout
    app.layout = html.Div(
        id="app-container",
        children=[
            # Left column
           
                    
            html.Div(
                id="left-column",
                className="three columns",
                children=make_menu_layout()
            ),

            # Right column
            html.Div(
                id="right-column",
                className="nine columns",
                
                children=[
                    # Dropdowns for X and Y axis of Scatterplot
                    html.H1('Strikershield: Goalkeeper Performance Dashboard', style={'textAlign': 'center'}),
                    html.H2('Scatterplot Configuration'),
                    html.H4('Select two variables to closer inspect the distribution of'),
                    html.Div([
                        dcc.Dropdown(
                            id='x-axis-dropdown',
                            options=[{'label': col, 'value': col} for col in df_player_keepersadv.columns],
                            value='goals against',  # default value
                            placeholder="Select X-axis"
                        ),
                        dcc.Dropdown(
                            id='y-axis-dropdown',
                            options=[{'label': col, 'value': col} for col in df_player_keepersadv.columns],
                            value='minutes 90s',  # default value
                            placeholder="Select Y-axis"
                        )
                    ]),
                    dcc.Graph(id='scatterplot-graph'),  # Placeholder for scatterplot
                    html.H2('Correlation Heatmap'),
                    html.H4('Select what variables you want to include in the heatmap'),
                    dcc.Dropdown(
                        id='column-select-dropdown',
                        options=[{'label': col, 'value': col} for col in df_player_keepersadv.columns],
                        multi=True,
                        value=[]
                    ),
                    dcc.Graph(id='heatmap'),
                    
                    html.H2('Radar Chart Configuration'),
                    html.H4('Here you can select the attributes you want in the plot and what player(s) you want displayed'),
                    # Dropdown for selecting variables for the Radar Chart
                    dcc.Dropdown(
                        id='radar-chart-dropdown',
                        options=[{'label': col, 'value': col} for col in df_player_keepersadv.columns if col != 'player'],
                        multi=True,
                        placeholder="Select variables for Radar Chart"
                    ),

                    # Dropdown for selecting players for the Radar Chart, with multi-selection enabled
                    dcc.Dropdown(
                        id='player-dropdown',
                        options=[{'label': player, 'value': player} for player in df_player_keepersadv['player'].unique()],
                        multi=True,  # Allow multiple players to be selected
                        placeholder="Select player(s)"
                    ),
                    dcc.Graph(id='radar-chart'),
                ],
            ),
        ],
    )

    # Callback for Heatmap
    @app.callback(
        Output('heatmap', 'figure'),
        [Input('column-select-dropdown', 'value')]
    )
    def update_heatmap(selected_columns):
        if not selected_columns:
            return px.imshow(pd.DataFrame())  # Empty plot if no columns are selected
        heatmap_data = df_player_keepersadv[selected_columns]
        corr_matrix = heatmap_data.corr()
        fig = px.imshow(corr_matrix, text_auto=True)
        return fig

    # Callback for Scatterplot
    @app.callback(
        Output('scatterplot-graph', 'figure'),
        [Input('x-axis-dropdown', 'value'),
         Input('y-axis-dropdown', 'value')]
    )
    def update_scatter_plot(x_axis, y_axis):
        if not x_axis or not y_axis:
            return px.scatter()  # Empty plot if axes are not selected
        fig = px.scatter(df_player_keepersadv, x=x_axis, y=y_axis)  # Create the figure using Plotly Express
        return fig


    # Callback for Radar Chart
    @app.callback(
        Output('radar-chart', 'figure'),
        [Input('radar-chart-dropdown', 'value'),
         Input('player-dropdown', 'value')]
    )
    def update_radar_chart(selected_variables, selected_players):
        if not selected_variables or not selected_players:
            return px.line_polar()  # Return an empty plot if no variables or players are selected

        # Initialize an empty list to hold all the traces
        traces = []

        # Loop through selected players and add a trace for each
        for player in selected_players:
            # Filter data for the selected player
            filtered_data = df_player_keepersadv[df_player_keepersadv['player'] == player]

            # Check if there's data for the selected player
            if not filtered_data.empty:
                # Prepare data for radar chart
                radar_values = filtered_data[selected_variables].iloc[0]
                traces.append(
                    go.Scatterpolar(
                        r=radar_values,
                        theta=selected_variables,
                        fill='toself',
                        name=player
                    )
                )

        # Create the figure with all the traces
        fig = go.Figure(data=traces)
        fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)

        return fig

    # Running the app
    if __name__ == '__main__':
        app.run_server(debug=False, dev_tools_ui=False)