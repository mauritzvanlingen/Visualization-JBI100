from jbi100_app.main import app
from jbi100_app.views.parallel_charts_adapted import ViolinPlots

from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Initialize necessary components for dash graphing
vp = ViolinPlots(path=r"C:\Users\ljpsm\OneDrive\kopie van afbeeldingen en documenten\Documenten\MotivationGPT\Visualization-JBI100\data-used.csv")

features = [# "team", 
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
    
    app.layout = html.Div(
        id="app-container",
        children=[
            # Right column
            html.Div(
                id="right-column",
                className="nine columns",
                children=[
                    dcc.Graph(id='violin-plot', 
                              figure = vp.figure(
                                features, 
                                teams
                              ),
                              style={'height': '90vh'}
                    )]
            ),
        ],
    )

    app.run_server(debug=False, dev_tools_ui=True)