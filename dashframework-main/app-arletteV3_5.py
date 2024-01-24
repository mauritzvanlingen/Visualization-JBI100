import dash
import dash_leaflet as dl
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
from helperFunctionsArletteV2 import corr_plots, create_merged_df,  get_cats #, figure_pa
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from jbi100_app.views.parallel_charts_adapted import ViolinPlots
import plotly.express as px
from jbi100_app.views.Menu_app import make_menu_layout
from jbi100_app.views.Worldmap import generate_map, calculate_center, geojson_layer
import json

# Define the style for the hovering menu
menu_style = {
    'position': 'absolute',  # Keep it positioned absolutely to float over the map
    'top': '10px',  # Keep the top position as is
    'right': '10px',  # Use 'right' instead of 'left' to align to the right side
    'width': '30vw',  # Menu width as 30% of the viewport width
    'height': '40vh',  # Menu height as 40% of the viewport height
    'background': 'rgba(255, 255, 255, 0.5)',  # White background with 50% opacity
    'padding': '10px',
    'borderRadius': '5px',  # Optional: rounded corners for the menu
    'zIndex': '1000',  # Ensure it sits on top of other elements
    'overflow': 'auto'  # Add scroll for overflow content
}


map_style = {
    'width': '100%',  # Map width is 100% of its container
    'height': 'calc(100vh - 20px)',  # Adjust the height based on your layout
    # You can use calc(100vh - header_height) if you have a header
    'margin': 'auto',  # Center the map within the column
}

# Load the modified GeoJSON data
df = pd.read_csv('../Data/dataset_teams.csv', delimiter=',')
team_to_country = df.set_index('team')['country'].to_dict()
ranking = pd.read_csv('../Data/FIFA World Cup Historic/fifa_ranking_2022-10-06.csv')

with open('../Data/modified_countries2.geojson', 'r') as f:
    geojson_data = json.load(f)

vp = ViolinPlots("../Data/data-used.csv")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

df_merge = create_merged_df()
df_merge = df_merge.reset_index()
feat_cats = get_cats()
feat_columns = []
for category_columns in feat_cats.values():
        feat_columns += category_columns

# Define a color dictionary outside of the callback
country_colors = {country: color for country, color in zip(df_merge['team'].unique(), px.colors.qualitative.Plotly)}

with open('../Data/modified_countries2.geojson', 'r') as f:
    geojson_data = json.load(f)
def create_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Feature Correlations")),
            dbc.ModalBody(dcc.Graph(id='imageCorr', figure=[corr_plots(0)])
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
            dbc.CardHeader(html.H2("Explore Category", className='text-white', style={'fontSize': '1.5em'})),
            dbc.CardBody([
                dbc.Button('Defense', id='btn-1', color="secondary", className="me-1", n_clicks=0, style = {'background-color': 'darkgreen'}),
                dbc.Button('Possession', id='btn-2', color="secondary", className="me-1", n_clicks=0),
                
                dbc.Button('Attack', id='btn-3', color="secondary", className="me-1", n_clicks=0),
                html.Hr(className='bg-light'),
                    dbc.Row([
                    dbc.Button("Feature-rank correlations", id="open-modal-btn", color='secondary', className="me-1", n_clicks=0)]),
                    html.Hr(className='bg-light'),
                html.H2('Select Feature(s)', className='text-white', style={'fontSize': '1.5em'}),
                dcc.Dropdown(id='feature_dd', options=[{'label': feat, 'value': feat} for feat in feat_columns], style={'color': 'black'}, multi= True), 
                html.H2('Undo normalization', className='text-white', style={'fontSize': '1.5em'}),
        dbc.Checklist(
        options=[
            {"label": "", "value": 1}
        ],
        value=[],
        id="normalize-toggle",
        switch=True,
    ),
    html.Div(id='normalize-label', children='Using Normalized Data', className='text-white'),
            ])
        ], color="dark"), width=4),
        dbc.Col(dcc.Graph(id='plot'), id='plot_con'),

            html.Label("Select country"),
            dcc.Dropdown(id='country-select-dropdown',
                 options=[{'label': team, 'value': team} for team in sorted(df_merge['team'].unique())],
                 style={'color': 'black'},
                 multi=True,
                 value=None),
    ]),

    html.Br(style={"line-height": "5"}),
    dbc.Row([
        html.Div(
            [
                generate_map(),  # This creates the map component
                html.Div(  # This creates the overlay menu
                    id="overlay-menu",
                    children=make_menu_layout(),
                    style=menu_style,
                )
            ],
            style={'position': 'relative'}  # Needed for correct positioning of the overlay
        )

    ]),
]))

@app.callback(
    [dash.dependencies.Output("image-modal", "is_open")],
    [dash.dependencies.Input("open-modal-btn", "n_clicks")],
    [dash.dependencies.State("image-modal", "is_open")]
)
def toggle_modal(n1, is_open):
    if n1:
        return [True]
    else:
        return [False]

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
            fig = corr_plots(0)
        elif button_id == "btn-2":
            fig = corr_plots(1)
        elif button_id == "btn-3":
            fig = corr_plots(2)
        return [fig]

    return existing_figure


@app.callback(
    [Output('plot', 'figure'),
     Output('plot', 'style'),
     Output('plot_con', 'style')],
    [Input('feature_dd', 'value'),
     Input('country-select-dropdown', 'value'),
     Input('normalize-toggle', 'value')]
)

def update_violin_plot_with_countries(selected_features, selected_countries, normalize):
    # Correctly set the normalization flag based on the toggle
    use_normalized_data = not (1 in normalize)

    # Initialize figure
    fig = go.Figure()

    # Check if at least one feature is selected
    if not selected_features:
        # Provide a default empty figure layout if no features are selected
        fig.update_layout(
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
        # Ensure selected_features is a list for consistent processing
        if not isinstance(selected_features, list):
            selected_features = [selected_features]

        # Process each feature to create the corresponding violin plot
        for feature in selected_features:
            # Obtain the data for the feature
            data = df_merge[feature]
            if use_normalized_data:
                # Apply normalization to the data
                mean = data.mean()
                std_dev = data.std()
                data = (data - mean) / std_dev

            # Add the violin plot for the feature
            fig.add_trace(go.Violin(
                y=data,
                name=feature,
                line_color='black',
                fillcolor='grey',
                box_visible=True,
                meanline_visible=True,
                showlegend=False  # Optionally hide the legend for each violin
            ))




        # Process selected countries to add their data points to the plot
        if selected_countries:
            # Initialize a dictionary to keep track of whether a country's legend item has been added
            country_legend_added = {country: False for country in selected_countries}
            for country in selected_countries:
                country_color = country_colors.get(country, 'black')
                for feature in selected_features:
                    country_data = df_merge[df_merge['team'] == country][feature]
                    # Normalize country-specific data if the toggle is on
                    if use_normalized_data:
                        country_data = (country_data - df_merge[feature].mean()) / df_merge[feature].std()

                    # Check if the legend item has already been added for this country
                    showlegend = not country_legend_added[country]

                    # Add scatter plot for the country data points
                    fig.add_trace(go.Scatter(
                        x=[feature] * len(country_data),
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
            title_text='Violin Plots for Selected Features and Countries',
            yaxis_title='Standard deviations from the mean' if use_normalized_data else 'Raw values',
            showlegend=True,
            margin=dict(l=10, r=10, t=50, b=10),
            height=450,
            width=950
        )



    return fig, {'display': 'block'}, {'display': 'block', 'width': '100%'}


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
        options = [{'label': feat, 'value': feat} for feat in list_feat]
        return [{'background-color': 'darkgreen'}, {}, {}, options]
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        selected_style = {'background-color': 'darkgreen'}
        default_style = {}

        if button_id == 'btn-1':
            list_feat = feat_cats["defense"]
            options = [{'label': feat, 'value': feat} for feat in list_feat]
            return [selected_style, default_style, default_style, options]
        elif button_id == 'btn-2':
            list_feat = feat_cats["possession"]
            options = [{'label': feat, 'value': feat} for feat in list_feat]
            return [default_style, selected_style, default_style, options]
        elif button_id == 'btn-3':
            list_feat = feat_cats["attack"]
            options = [{'label': feat, 'value': feat} for feat in list_feat]
            return [default_style, default_style, selected_style, options]

@app.callback(
    Output("geojson", "hideout"),
    Output("country-select-dropdown", "options"),
    [Input('rank-slider', 'value')])

def update_geojson_style(selected_range):
    min_rank, max_rank = selected_range
    filtered_df = ranking[(ranking['rank'] >= min_rank) & (ranking['rank'] <= max_rank)]
    opt = [{'label': team, 'value': team} for team in sorted(filtered_df['team'].unique())]
    return {"min_rank": min_rank, "max_rank": max_rank}, opt

@app.callback(
    [Output("map", "center"),
     Output("map", "zoom"),
     Output("map", "children"),
     ],  # Update this to change the map's children
    [Input('dropdown_search', 'value')]
)
def update_map_on_team_select(selected_team):
    default_zoom = 2
    default_center = [20, 0]
    map_children = [dl.TileLayer(), geojson_layer]  # Include default layers

    if selected_team is None:
        return default_center, default_zoom, map_children

    selected_country = team_to_country.get(selected_team, None)
    if selected_country:
        for feature in geojson_data['features']:
            if feature['properties']['ADMIN'] == selected_country:
                country_center = calculate_center(feature['geometry'])
                new_zoom = 5
                marker = dl.Marker(position=country_center, children=dl.Tooltip(selected_country))
                map_children.append(marker)  # Add the marker to children
                return country_center, new_zoom, map_children

    return default_center, default_zoom, map_children


if __name__ == '__main__':
    app.run_server(debug=True)





