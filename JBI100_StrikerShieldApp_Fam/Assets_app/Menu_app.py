from dash import dcc, html
import pandas as pd
import dash_extensions as de
import folium

df = pd.read_csv('json_teamsmapped.csv', delimiter=',')
teams = sorted(df['team'].tolist())

def generate_description_card():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5("Menu"),
            html.Div(
                id="intro",
            ),
        ],
    )

def generate_dropdown_opponent():
    return html.Div(
        children=[
            html.Label("Select opponent"),
            dcc.Dropdown(id='dropdown_opponent',
                 options=[{'label': team, 'value': team} for team in teams],
                 multi=False,
                 value=None),

        ]
    )

def generate_dropdown_team():
    return html.Div(
        children=[
            html.Label("Select your own team"),
            dcc.Dropdown(id='dropdown_own_team',
                         options=[{'label': team, 'value': team} for team in teams],
                         multi=False,
                         value=None),

        ]
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
        ], style={"textAlign": "float-left"}
    )


def make_menu_layout():
    return [generate_description_card(), generate_control_card(), generate_dropdown_opponent()]
