import pandas as pd
import json
from dash_extensions.javascript import assign
import dash_leaflet as dl
import matplotlib.pyplot as plt
from jbi100_app.views.helperFunctionsApp import corr_plots, create_merged_df,  get_cats, get_descriptions, get_labels
import matplotlib.colors as mcolors
from dash import dcc, html
from geopy.geocoders import Nominatim

# Load the dataset

feat_cats = get_cats()

feat_columns = []
for category_columns in feat_cats.values():
    feat_columns += category_columns
feat_columns = list(set(feat_columns)) 
df_merge = create_merged_df(feat_columns)
df_merge = df_merge.reset_index()



df_json = pd.read_csv('../Data/dataset_teams.csv')
df = pd.merge(df_json, df_merge, on='team')
df.reset_index()

country_to_color = {}
for team in df['team']:
    country_to_color[team] = 'white'


# Load the GeoJSON data
with open('../Data/modified_countries2.geojson', 'r') as f:
    geojson_data = json.load(f)

style_handle = assign("""function(feature, context){    
    const country = feature.properties.ADMIN;
    const color_coun = context.hideout.countryToColor[country];                                           
    return {fillColor: color_coun, color: 'None', weight: 0.5, fillOpacity:1};
}""")

# Define the onEachFeature function
on_each_feature = assign("""function(feature, layer) {
    if (feature.properties && feature.properties.ADMIN) {
        layer.bindTooltip(feature.properties.ADMIN);
    }
}""")

# Create the GeoJSON layer
geojson_layer = dl.GeoJSON(
    data=geojson_data,
    id="geojson",
    hideout={
        'countryToColor': country_to_color
    },
    style=style_handle,
    onEachFeature=on_each_feature
)


def generate_map(map_center=[20, 0],map_zoom=2.5, marker=None):

    map_children = [
        dl.TileLayer(),
        geojson_layer]

    if marker:
        map_children.append(marker)

    return dl.Map(
        id="map",
        children=map_children,
        center=map_center,
        zoom=map_zoom,
        style={'width': '100%', 'height': '100vh'}
    )

def create_legend(min_val, max_val, cmap, feature_title):
    # Number of color steps in the legend
    num_steps = 10
    # Generate color steps
    color_steps = [cmap(i/num_steps) for i in range(num_steps + 1)]
    # Convert colors to hex
    color_steps = [mcolors.rgb2hex(color) for color in color_steps]
    # Generate labels for color steps
    labels = ['{:.2f}'.format(min_val + (max_val - min_val) * i/num_steps) for i in range(num_steps + 1)]

    # Create legend as a list of Dash HTML components
    legend = html.Div(
        style={
            'position': 'absolute',
             'right': '10px',
            'top': '10px',
            'zIndex': '1000',
            'backgroundColor': 'white',
            'padding': '15px',
            'border': '2px solid rgba(0,0,0,0.2)',
            'borderRadius': '8px',
            'boxShadow': '0 1px 5px rgba(0,0,0,0.4)',
            'fontSize': '14px',
            'fontFamily': 'Arial, sans-serif',
            'color': 'white',
            'opacity': '0.9'
        },
        children=[
            html.H4(get_labels(feature_title), style={'textAlign': 'center', 'marginBottom': '10px', 'color':'black'}),]+[  # Feature title
            html.Div(
                style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '8px'},
                children=[
                    html.Div(
                        style={'width': '30px', 'height': '30px', 'backgroundColor': color_steps[i]}
                    ),
                    html.Small(style={'marginLeft': '8px', 'color': 'black'}, children=labels[i])
                ]
            ) for i in range(num_steps + 1)
        ]
    )
    return legend


def get_country_from_latlng(lat, lng):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse((lat, lng), language='en')
    if location and 'country' in location.raw['address']:
        return location.raw['address']['country']
    return None
