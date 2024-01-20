from jbi100_app.main import app
from jbi100_app.views.parallel_charts_adapted import ViolinPlots

from dash import html, dcc, Dash

import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Initialize necessary components for dash graphing
vp = ViolinPlots(path=r"C:\Users\ljpsm\OneDrive\kopie van afbeeldingen en documenten\Documenten\MotivationGPT\Visualization-JBI100\data-used.csv")

features = ["team", 
            # "rank", 
            # "minutes", 
            "clearances",
            "blocked_passes",
            "blocked_shots",
            "dribble_tackles_pct",
            "tackles_interceptions",
            "errors",
            "miscontrols", 
            "passes_pct_short",
            "passes_pct_medium",
            "passes_pct_long",
            "passes_total_distance",
            "aerials_won_pct",
            "dispossessed", 
            "shots_on_target_per90", 
            "shots_on_target_pct",
            "goals_per_shot_on_target",
            # "passes_into_penalty_area",
            # "crosses_into_penalty_area",
            # "touches_att_pen_area",
            "xg_per90",
            "average_shot_distance",
            ]

teams = [
    "Argentina",
    "France"
]

if __name__ == '__main__':

    app.layout = dbc.Container(style={'width': '80%', 'margin': '0 auto',  'font-family': 'verdana'}, fluid=True, children=[

        # Title
        dbc.Row(dbc.Col(html.H1("StrikerShield", className='text-center my-4 text-white'), width=14, style= {'font-family': 'Broadway', 'marginTop': '5px'})),

        # Buttons to select teams and features
        dbc.Row([
            # Select team button
            dbc.Col(dbc.Button('Browse teams', id='team-button', color="warning", n_clicks=0, style = {'background-color': 'darkgreen', 'border-color': 'darkgreen', 'float': 'right'})),
            # Select feature button
            dbc.Col(dbc.Button('Browse features', id='feature-button', color="warning", n_clicks=0, style = {'background-color': 'darkgreen', 'border-color': 'darkgreen'})),
        ]),

        # Extra space between buttons and feature
        html.Br(),

        # Violin plots
        dbc.Row(html.Div(id="right-column",
                         className="nine columns",
                         children=[
                            dcc.Graph(id='violin-plot', 
                                      figure = vp.figure(
                                        features, 
                                        teams
                                      ),
                                      style={'height': '75vh'})
                          ]))

        ])
    
    app.run_server(debug=False, dev_tools_ui=True)


# Feature pop-up
