import dash
import dash_leaflet as dl
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

import plotly.graph_objs as go
import pandas as pd
import plotly.express as px
import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

from jbi100_app.views.helperFunctionsApp import corr_plots, create_merged_df,  get_cats, get_descriptions, get_labels, getFeatFromLabel
from jbi100_app.views.Menu_app import make_menu_layout
from jbi100_app.views.WorldmapV2 import generate_map, geojson_layer, create_legend, get_country_from_latlng
from geopy.geocoders import Nominatim
import matplotlib.cm as cm

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

map_style = {
    'width': '100%',  # Map width is 100% of its container
    'height': 'calc(100vh - 20px)',  # Adjust the height based on your layout
    # You can use calc(100vh - header_height) if you have a header
    'margin': 'auto',  # Center the map within the column
}

WIDTH_VIOLIN_PLOTS = 800

feat_cats = get_cats()

feat_columns = []
for category_columns in feat_cats.values():
    feat_columns += category_columns
feat_columns = list(set(feat_columns)) 
feature_descriptions = {}
for item in feat_columns:
    feature_descriptions[item] = item

     
df_merge = create_merged_df(feat_columns)
df_merge = df_merge.reset_index()



# Load the modified GeoJSON data
df = pd.read_csv('../Data/dataset_teams.csv', delimiter=',')
team_to_country = df.set_index('team')['country'].to_dict()
ranking = pd.read_csv('../Data/FIFA World Cup Historic/fifa_ranking_2022-10-06.csv')
ranking = ranking[ranking['team'].isin(df_merge['team'])]

df_merge_json = pd.merge(df, df_merge, on='team')


with open('../Data/modified_countries2.geojson', 'r') as f:
    geojson_data = json.load(f)


# Define a color dictionary outside of the callback
cmap = plt.get_cmap('tab20b', len(df_merge['team'])+1)
colors = cmap(np.linspace(0, 1, len(df_merge['team'])+1))
hex_colors = [cm.colors.rgb2hex(color) for color in colors]

country_colors = {}
i = 0 
for country in df_merge['team']:
    country_colors[country] = hex_colors[i]
    i = i + 1 


with open('../Data/modified_countries2.geojson', 'r') as f:
    geojson_data = json.load(f)


def create_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Feature Correlations"), style={'width':'800px'}),
            dbc.ModalBody(dcc.Graph(id='imageCorr', figure=[corr_plots('defense', feat_cats, df_merge)]), style={'width':'800px'}
            ),
        ],
        id="image-modal",
        is_open=False
    )


app.layout = (
    dbc.Container(style={'width': '80%', 'margin': '0 auto',  'font-family': 'verdana'}, fluid=True, children=[
    create_modal(),
    dbc.Row(dbc.Col(html.H1("StrikerShield", className='text-center my-4 text-white'), width=14, style= {'font-family': 'Broadway', 'marginTop': '30px'})),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H2("Choose Category", className='text-white', style={'fontSize': '1.5em'}),
                dbc.Button('Defense', id='btn-1', color="secondary", className="me-1", n_clicks=0, style = {'background-color': 'darkgreen'}),
                dbc.Button('Possession', id='btn-2', color="secondary", className="me-1", n_clicks=0),
                
                dbc.Button('Attack', id='btn-3', color="secondary", className="me-1", n_clicks=0),
                html.Hr(className='bg-light'),
                html.H2('Select Feature(s)', className='text-white', style={'fontSize': '1.5em'}),
                html.Div(id='text1', children='Click on one of the feature-rank correlation plots ', className='text-white'),
                    dbc.Row([
                    dbc.Button("Feature-Rank correlation plots", id="open-modal-btn", color='secondary', className="me-1", n_clicks=0)]),
                    html.Div(id='text2', children='Or select features manually', className='text-white'),
                                   
                dcc.Dropdown(id='feature_dd', options=[{'label': feat, 'value': feat} for feat in feat_columns], style={'color': 'black'}, multi= True),
                html.Hr(className='bg-light'), 
                html.H2('Choose Raw or Min-Max Scaled Data', className='text-white', style={'fontSize': '1.5em'}),
        dbc.Checklist(
        options=[
            {"label": "", "value": 1}
        ],
        value=[],
        id="normalize-toggle",
        switch=True,
    ),
    html.Div(id='normalize-label', children='Using Min-Max Scaled Data', className='text-white'),
    html.Hr(className='bg-light'),
        html.H2('Select Countries to Compare', className='text-white', style={'fontSize': '1.5em'}),
         html.Div(id='text3', children='Select features manually', className='text-white'),

            dcc.Dropdown(id='country-select-dropdown',
                 options=[{'label': team, 'value': team} for team in sorted(df_merge['team'].unique())],
                 style={'color': 'black'},
                 multi=True,
                 value=None), html.Div(id='text4', children='Or click on a country in the map below', className='text-white')]
                 )
        
        ], color="dark"), width=4),
        dbc.Col(dcc.Graph(id='plot'), id='plot_con')

    ]),

    html.Br(style={"line-height": "5"}),
    dbc.Row([
        html.Div(
            [
                generate_map(),  # This creates the map component
                html.Div(  # This creates the overlay menu
                    id='legend-container'
                )
            ],
            style={'position': 'relative'}  # Needed for correct positioning of the overlay
        )

    ]),
    html.Div(id='selected-feature-map', style={'display': 'none'})
]))

@app.callback(
    Output('selected-feature-map', 'children'),
    [Input('plot', 'clickData')],
    [State('feature_dd', 'options')])
def display_click_data(clickData, feature_options):
    if clickData is not None:
        label = clickData['points'][0]['x']
        feature_label = getFeatFromLabel(label)
        return feature_label
    else:
        raise PreventUpdate

@app.callback(
    [Output("image-modal", "is_open"),
     Output("feature_dd", "value")],
    [Input("open-modal-btn", "n_clicks"),
     Input("imageCorr", "clickData")],
    [State("image-modal", "is_open"),
     State('feature_dd', 'options'),
     State("feature_dd", "value")]
)
def toggle_modal(n1, clicked, is_open, feature_options, current_value):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # If the button to open the modal was clicked
    if trigger_id == "open-modal-btn":
        return [not is_open, dash.no_update]  # Toggle the modal, no change to dropdown

    # If a point on the correlation plot was clicked
    elif trigger_id == "imageCorr" and clicked:
        # Use the point's customdata or text/label to match the feature name
        feat_idx = clicked['points'][0]['curveNumber']
        clicked_feat_label = feature_options[feat_idx]['label']
        # Find the corresponding feature value (if the label is the feature name itself, you can directly use it)
        clicked_feat_value = getFeatFromLabel(clicked_feat_label)  # Assuming this function returns the feature name
        # Update the dropdown to show the clicked feature (append if multiselect is allowed)
        if current_value is not None and isinstance(current_value, list):
            return [is_open, current_value + [clicked_feat_value]]
        else:
            return [is_open, [clicked_feat_value]]

    # Default return (covers initial load and other unspecified conditions)
    return [is_open, dash.no_update]


@app.callback(
    [Output("imageCorr", "figure")],
    [Input("btn-1", "n_clicks"), Input("btn-2", "n_clicks"), Input("btn-3", "n_clicks")],
    [State("imageCorr", "figure")],
)
def update_graph(btn1, btn2, btn3, existing_figure):
    ctx = dash.callback_context
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id in ["btn-1", "btn-2", "btn-3"]:
        if button_id == "btn-1":
            fig = corr_plots('defense', feat_cats, df_merge)
        elif button_id == "btn-2":
            fig = corr_plots('possession', feat_cats, df_merge)
        elif button_id == "btn-3":
            fig = corr_plots('attack', feat_cats, df_merge)
        return [fig]

    return existing_figure


@app.callback(
    [Output('plot', 'figure'),
     Output('plot', 'style'),
     Output('plot_con', 'style'),
     Output('country-select-dropdown', 'value')],
    [Input('feature_dd', 'value'),
     Input('normalize-toggle', 'value'),
     Input('imageCorr', 'clickData'),
     Input('map', 'clickData'),
     Input('country-select-dropdown', 'value')],
     [State('feature_dd', 'options')]
)
def update_violin_plot_with_countries(selected_features, normalize, corrClick, mapClick, selected_countries, feature_options):
    if mapClick:
        lat = mapClick['latlng']['lat']
        lng = mapClick['latlng']['lng']
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.reverse((lat, lng), language='en')
        countryClicked = location.raw['address']['country']
        if selected_countries == None:
            selected_countries = [countryClicked]
        else:
            if countryClicked not in selected_countries:
                selected_countries.append(countryClicked)

    use_normalized_data = not (1 in normalize)

    # Initialize figure
    fig = go.Figure()

    # Check if at least one feature is selected
    if not selected_features:
        # Provide a default empty figure layout if no features are selected
        fig.update_layout(
            height=600,
            width=WIDTH_VIOLIN_PLOTS,
            title_text='Please select at least one feature to visualize.',
            xaxis={'visible': False},
            yaxis={'visible': False},
            annotations=[{
                'text': 'No features selected',
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {'size': 28}
            }]
        )
    else:
        # Process each feature to create the corresponding violin plot
        for feature in selected_features:
            # Obtain the data for the feature
            data = df_merge[feature]

            if use_normalized_data:
                # Apply normalization to the data
                # mean = data.mean()
                # std_dev = data.std()
                # data = (data - mean) / std_dev
                min_val = data.min()
                max_val = data.max()
                data = (data - min_val)/(max_val-min_val)
                ytitle = 'Min-max scaled values'
            else:
                ytitle = 'Raw values'

            # Add the violin plot for the feature
            fig.add_trace(go.Violin(
                y=data,
                name=get_labels(feature),
                line_color='black',
                fillcolor='grey',
                box_visible=True,
                meanline_visible=True,
                showlegend=False  # Optionally hide the legend for each violin
        
            ))
            desc = get_descriptions(feature)
            fig.add_annotation(
            x=get_labels(feature),
            y=-0.12,
            xref='x',
            yref='paper',
            text="&#9432;",  # Unicode character for information icon
            showarrow=False,
            font=dict(
                size=16,
                color="black"
            ),
            hovertext=desc,  # Your description here
            hoverlabel=dict(
                bgcolor="white",
                font_size=20,
                font_family="Arial"
            )
        )
        
        # Process selected countries to add their data points to the plot
        if selected_countries:
            

            # Initialize a dictionary to keep track of whether a country's legend item has been added
            country_legend_added = {country: False for country in selected_countries}
            for country in selected_countries:
                country_color = country_colors.get(country)
                for feature in selected_features:
                    country_data = df_merge[df_merge['team'] == country][feature]
                    # Normalize country-specific data if the toggle is on
                    if use_normalized_data:
                        #country_data = (country_data - df_merge[feature].mean()) / df_merge[feature].std()
                        country_data = (country_data - df_merge[feature].min())/(df_merge[feature].max() - df_merge[feature].min())

                    # Check if the legend item has already been added for this country
                    showlegend = not country_legend_added[country]

                    # Add scatter plot for the country data points
                    fig.add_trace(go.Scatter(
                        x=[get_labels(feature)] * len(country_data),
                        y=country_data,
                        mode='markers',
                        marker=dict(color=country_color, size=10),
                        name=country if showlegend else '',  # Only add country name for legend if not already added
                        legendgroup=country,  # Group all markers of the same country
                        showlegend=showlegend  # Only show legend item once per country
                    ))

                    # Mark this country's legend as added
                    country_legend_added[country] = True

        # Update the layout of the figure
        fig.update_layout(
            title_text='Click on violin plot to visualise feature values in map',
            #yaxis_title='Standard deviations from the mean' if use_normalized_data else 'Raw values',
            yaxis_title=ytitle,
            showlegend=True,
            margin=dict(l=10, r=10, t=50, b=60),
            height=600,
            width=WIDTH_VIOLIN_PLOTS,
        )

    return fig, {'display': 'block'}, {'display': 'block', 'width': '10%'}, selected_countries


@app.callback(
    Output('normalize-label', 'children'),
    [Input('normalize-toggle', 'value')])

def update_normalize_label(normalize):
    # Update the label based on the toggle state
    if 1 in normalize:
        return 'Using Raw Data'
    else:
        return 'Using Normalized Data'
@app.callback(
    [Output('btn-1', 'style'),
     Output('btn-2', 'style'),
     Output('btn-3', 'style'),
     Output('feature_dd', 'options')],
    [Input('btn-1', 'n_clicks'),
     Input('btn-2', 'n_clicks'),
     Input('btn-3', 'n_clicks')])

def update_button_styles(btn1, btn2, btn3):
    ctx = dash.callback_context

    if not ctx.triggered:
        list_feat = feat_cats["defense"]
        options = [{'label': get_labels(feat), 'value': feat} for feat in list_feat]
        return [{'background-color': 'darkgreen'}, {}, {}, options]
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        selected_style = {'background-color': 'darkgreen'}
        default_style = {}

        if button_id == 'btn-1':
            list_feat = feat_cats["defense"]
            options = [{'label': get_labels(feat), 'value': feat} for feat in list_feat]
            return [selected_style, default_style, default_style, options]
        elif button_id == 'btn-2':
            list_feat = feat_cats["possession"]
            options = [{'label': get_labels(feat), 'value': feat} for feat in list_feat]
            return [default_style, selected_style, default_style, options]
        elif button_id == 'btn-3':
            list_feat = feat_cats["attack"]
            options = [{'label': get_labels(feat), 'value': feat} for feat in list_feat]
            return [default_style, default_style, selected_style, options]

@app.callback(
    [Output("geojson", "hideout"),
     Output("legend-container", "children")],
    [Input('selected-feature-map', 'children'),
     Input('normalize-toggle', 'value')])
def update_geojson_style(feat, normalize):
    if not feat:
        feat = "points"
        
    min_val = df_merge[feat].min()
    max_val = df_merge[feat].max()
    all_val = df_merge[feat]

    norm = plt.Normalize(min_val, max_val)
    cmap = plt.get_cmap('Purples')
    
    list_teams = list(df_merge['team'])
    dict_color = {}
    for idx in range(len(list_teams)):
        team = list_teams[idx]
        val = all_val.iloc[idx]
        dict_color[team] = mcolors.rgb2hex(cmap(norm(val)))
    # Create the legend
    if 1 in normalize:
        legend = create_legend(float((min_val)), float((max_val)), cmap, feat)
    else:
        legend = create_legend(float(norm(min_val)), float(norm(max_val)), cmap, feat)

    return {'countryToColor': dict_color}, legend




if __name__ == '__main__':
    app.run_server(debug=True)





