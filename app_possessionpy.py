from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd


# =============================================================================
# DATA IMPORT AND CLEANING

# Exclude goalkeepers as they are not in the field so not representable? 
# =============================================================================
df_player_possession = pd.read_csv('player_possession.csv', delimiter=',')
filtered_df = df_player_possession[df_player_possession['position'] != 'GK']


# =============================================================================
# TYPES OF AREAS AND EXPLANATION 

# "touches":string"Number of times a player touched the ball. Note: Receiving a pass, then dribbling, then sending a pass counts as one touch"
# "touches_def_pen_area":string"Touches in defensive penalty area"
# "touches_def_3rd":string"Touches in defensive 1/3"
# "touches_mid_3rd":string"Touches in middle 1/3"
# "touches_att_3rd":string"Touches in attacking 1/3"
# "touches_att_pen_area":string"Touches in attacking penalty area"
# "touches_live_ball":string"Live-ball touches. Does not include corner kicks, free kicks, throw-ins, kick-offs, goal kicks or penalty kicks"
# =============================================================================

touch_areas = ['touches_def_pen_area', 'touches_def_3rd', 'touches_mid_3rd', 'touches_att_3rd', 'touches_att_pen_area', 'touches_live_ball']
teams = ['Argentina', 'Australia', 'Belgium', 'Brazil', 'Cameroon', 'Canada', 'Costa Rica', 'Croatia', 'Denmark', 'Ecuador', 'England', 'France', 'Germany', 'Ghana', 'IR Iran', 'Japan', 'Korea Republic', 'Mexico', 'Morocco', 'Netherlands', 'Poland', 'Portugal', 'Qatar', 'Saudi Arabia', 'Senegal', 'Serbia', 'Spain', 'Switzerland', 'Tunisia', 'United States', 'Uruguay', 'Wales']
area_labels = {
    'touches_def_pen_area': 'Touches in defensive penalty area',
    'touches_def_3rd': 'Touches in defensive 1/3',
    'touches_mid_3rd': 'Touches in middle 1/3',
    'touches_att_3rd': 'Touches in attacking 1/3',
    'touches_att_pen_area': 'Touches in attacking penalty area',
    'touches_live_ball': 'Live-ball touches'
}
# =============================================================================
# START APPLICATION 
# =============================================================================
app = Dash(__name__)

# =============================================================================
# LAYOUT OF APPLICATION 
# =============================================================================
app.layout = html.Div([
    html.H1(children="Possession of ball per area", style={'textAlign':'center'}),
    html.Br(),
    
    dcc.Dropdown(id='dropdown_team_1', 
                 options=[{'label': team, 'value': team} for team in teams],
                 multi=False,
                 value='Argentina'),
    
    html.Br(),
    dcc.Dropdown(id='dropdown_team_2', 
                 options=[{'label': team, 'value': team} for team in teams],
                 multi=False,
                 value='France'),
    
    html.Br(),
    
    dcc.Dropdown(id='dropdown_area', 
                 options=[{'label': 'Touches in defensive penalty area', 'value': 'touches_def_pen_area'},
                          {'label': 'Touches in defensive 1/3', 'value': 'touches_def_3rd'},
                          {'label': 'Touches in middle 1/3', 'value': 'touches_mid_3rd'},
                          {'label': 'Touches in attacking 1/3', 'value': 'touches_att_3rd'},
                          {'label': 'Touches in attacking penalty area', 'value': 'touches_att_pen_area'},
                          {'label': 'Live-ball touches', 'value': 'touches_live_ball'}],
                 multi=False,
                 value='touches_def_pen_area'),
    
    html.Br(),
    dcc.Graph(id='figure-content')

])

# =============================================================================
# INTERACTION (CALLBACK)
# =============================================================================
@app.callback(
    Output('figure-content', 'figure'),
    Input('dropdown_team_1', 'value'),
    Input('dropdown_team_2','value'),
    Input('dropdown_area','value')
)

# =============================================================================
# UPDATE FIGUUR OP BASIS VAN INTERACTIE 
# =============================================================================
def update_graph(value_team_1,value_team_2, value_area):
    filtered_data = filtered_df[filtered_df['team'].isin([value_team_1, value_team_2])]
    grouped_data = filtered_data.groupby(['team', 'position']).agg({
        value_area: 'sum'
    }).reset_index()

    area_label = area_labels.get(value_area, value_area)
    
    fig = px.bar(
        data_frame=grouped_data,
        x='position',
        y=value_area,
        color='team',
        barmode='group',
        title=f'{area_label} by position {value_team_1} vs. {value_team_2}',
        labels={'position': 'Position', value_area: 'Number of Touches'}
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False)
