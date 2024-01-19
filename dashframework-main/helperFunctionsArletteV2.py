import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import plotly.graph_objs as go
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
import plotly
import plotly.express as px
import plotly.graph_objs as go

def get_cats():
    return {'defense': ["clearances",
                "blocked_passes",
                "blocked_shots",
                "dribble_tackles_pct",
                "tackles_interceptions",
                "errors",
                "miscontrols"], 'possession':
                ["passes_pct_short",
                "passes_pct_medium",
                "passes_pct_long",
                "passes_total_distance",
                "aerials_won_pct",
                "dispossessed" ],
                'attack':
                ["rank", "shots_on_target_per90", 
                "shots_on_target_pct",
                "goals_per_shot_on_target",
                "passes_into_penalty_area",
                "crosses_into_penalty_area",
                "touches_att_pen_area",
                "xg_per90",
                "average_shot_distance",
                ]}
    

def create_merged_df():
    features = ["team", 
                "rank", 
                "minutes", 
                "clearances",
                "blocked_passes",
                "blocked_shots",
                "dribble_tackles_pct",
                "tackles_interceptions",
                "errors",
                "miscontrols", "passes_pct_short",
                "passes_pct_medium",
                "passes_pct_long",
                "passes_total_distance",
                "aerials_won_pct",
                "dispossessed", "shots_on_target_per90", 
                "shots_on_target_pct",
                "goals_per_shot_on_target",
                "passes_into_penalty_area",
                "crosses_into_penalty_area",
                "touches_att_pen_area",
                "xg_per90",
                "average_shot_distance",
                ]
    
    df_team = pd.read_csv(r'Data/FIFA World Cup 2022 Team Data/team_data.csv', delimiter=',')
    df_fifa = pd.read_csv(r'Data/FIFA World Cup Historic/fifa_ranking_2022-10-06.csv', delimiter=',')
    # Merge dataframes and select features 
    merged_df = pd.merge(df_team, df_fifa, on='team')
    red_mer_df = merged_df[features].copy()
    red_mer_df = red_mer_df.set_index('team')
    print(merged_df['team'])

    # Check NaN values, negative values and <3 matches played

    # print(red_mer_df.isna().sum().sum())
    # print((red_mer_df['minutes'] < 270).sum().sum())
    # print((red_mer_df < 0).sum().sum())

    # Normalize data by dividing by nr of matches played
    norm_df = red_mer_df.copy()
    
    norm_df['nr_match'] = norm_df['minutes']/90
    norm_df = norm_df.apply(lambda row: row / row['nr_match'], axis=1)
    
    norm_df['minutes'] = red_mer_df['minutes']
    norm_df['rank'] = red_mer_df['rank']
    return norm_df

def corr_plots(idx):
    list_features = ['defense', 'possession', 'attack']
    cats = [["rank", "clearances",
                "blocked_passes",
                "blocked_shots",
                "dribble_tackles_pct",
                "tackles_interceptions",
                "errors",
                "miscontrols"
            ],["rank", 
                "passes_pct_short",
                "passes_pct_medium",
                "passes_pct_long",
                "passes_total_distance",
                "aerials_won_pct",
                "dispossessed" ],
                ["rank", "shots_on_target_per90", 
                "shots_on_target_pct",
                "goals_per_shot_on_target",
                "passes_into_penalty_area",
                "crosses_into_penalty_area",
                "touches_att_pen_area",
                "xg_per90",
                "average_shot_distance",
                ]]

    df_team_data = pd.read_csv(r'Data/FIFA World Cup 2022 Team Data/team_data.csv', delimiter=',')
    df_historic_fifa_ranking = pd.read_csv(r'Data/FIFA World Cup Historic/fifa_ranking_2022-10-06.csv', delimiter=',')
    cat = cats[idx]
    rank_mapping = df_historic_fifa_ranking.set_index('team')['rank'].to_dict()
    df_team_data['rank'] = df_team_data['team'].map(rank_mapping)*-1
    numerical_df = df_team_data[cat].select_dtypes(include=['number'])
    scaler = StandardScaler()
    normalized_df = pd.DataFrame(scaler.fit_transform(numerical_df), columns=numerical_df.columns)
    correlations = numerical_df.drop('rank', axis=1).corrwith(numerical_df['rank'])
    cat.remove('rank')
    sorted_corrs = correlations[cat].sort_values(ascending=False)
    fig = go.Figure(data=[
        go.Bar(x=sorted_corrs.index, y=sorted_corrs, marker_color='blue')
    ])
    name_feat = list_features[idx]
    fig.update_layout(
        xaxis=dict(tickangle=-45),
        xaxis_title='Features',
        yaxis_title='Correlation',
        margin=dict(l=20, r=20, t=20, b=20)
    )

    return fig 

def figure_pa(attributes: list[str], *teams_to_compare: list[str]) -> plotly.graph_objs.Figure:
    df_filtered = create_merged_df()
    scaler = MinMaxScaler()
    df_filtered[attributes] = scaler.fit_transform(df_filtered[attributes])
    df_filtered = df_filtered[attributes] 
    df_filtered = df_filtered.loc[df_filtered.index.isin(teams_to_compare)] 
    df_filtered = df_filtered.reset_index()
    
    teams = df_filtered["team"].astype('category')
    df_filtered['team'] = teams.cat.codes

    color_scale = []
    colors = [[250,0,0], [0,0,250]]
    for i in range(2):
        color = f"rgb({colors[i][0]}, {colors[i][1]}, {colors[i][2]})"
        color_scale.append((i * 0.5, color))
        color_scale.append(((i+1) * 0.5, color))

    columns = [col for col in df_filtered.columns if col != "team"]

    color_scale_custom = []
    for i, team in enumerate(teams_to_compare):
        color = f"rgb({colors[i][0]}, {colors[i][1]}, {colors[i][2]})"
        color_scale_custom.append([i / len(teams_to_compare), color])
        color_scale_custom.append([(i + 1) / len(teams_to_compare), color])
                  
        fig = go.Figure(data=
            go.Parcoords(
                line=dict(
                    color=df_filtered['team'],
                    colorscale=color_scale_custom,
                    showscale=False,  
                ),
                dimensions=[
                    dict(label=col, values=df_filtered[col], 
                         ticktext= ['0', '0.5', '1'],
                         tickvals =[0, 0.5, 1]
                         ) for col in attributes
                ]
            )
        )
    for dimension in fig.data[0]['dimensions']:
        dimension['range'] = [0, 1]
    return fig
            