from dash import dcc, html
import pandas as pd


df = pd.read_csv('../Data/dataset_teams.csv')
teams = sorted(df['team'].tolist())


def generate_dropdown_search():
    return html.Div(
        children=[
            html.Label("Search country"),
            dcc.Dropdown(id='dropdown_search',
                         options=[{'label': team, 'value': team} for team in teams],
                         style={'color': 'black'},
                         multi=False,
                         value=None),


        ],
        style = {'color':'black'},
    )

def generate_control_card():
    """

    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.Label("Select range of FIFA ranking"),
            dcc.RangeSlider(
                id='rank-slider',
                min=df['rank'].min(),
                max=df['rank'].max(),
                step=1,
                marks={i: str(i) for i in range(df['rank'].min(), df['rank'].max() + 1, 10)},
                value=[df['rank'].min(), df['rank'].max()],
                tooltip={"placement": "bottom", "always_visible": True}

            ),
        ],

        style={'color' : 'black', "textAlign": "float-left"}
    )


def make_menu_layout():
    return [generate_control_card(), generate_dropdown_search()]
