from dash import dcc, html
import pandas as pd
import json
from dash_extensions.javascript import assign
import dash_leaflet as dl

df = pd.read_csv('json_teamsmapped.csv', delimiter=',')

with open('modified_countries.geojson', 'r') as f:
    geojson_data = json.load(f)

style_handle = assign("""function(feature, context){
    const {min_rank, max_rank} = context.hideout;
    const rank = feature.properties.rank;
    if(rank >= min_rank && rank <= max_rank){
        return {fillColor: 'red', color: 'grey', weight: 0.5};
    }
    return {fillColor: 'grey', color: 'grey', weight: 0.5};
}""")

def style_function(feature):
    if feature["properties"]["selected"]:
        # Get the rank of the feature
        rank = feature["properties"]["rank"]
        # Calculate a darker shade based on rank
        dark_color = calculate_darker_color(rank)
        return {"fillColor": dark_color, "color": "grey", "weight": 0.5}
    else:
        return {"fillColor": "grey", "color": "grey", "weight": 0.5}

def calculate_darker_color(rank):
    # Adjust the color based on the rank (you can customize this logic)
    # For example, make it darker as the rank increases
    dark_color = f"rgba(255, 0, 0, {0.2 + rank * 0.1})"  # Adjust the RGB values as needed
    return dark_color

def generate_map():
    # Define a JavaScript function for onEachFeature
    on_each_feature = assign("""function(feature, layer) {
        if (feature.properties && feature.properties.ADMIN) {
            layer.bindTooltip(feature.properties.ADMIN);
        }
    }""")

    # Define the GeoJSON component with onEachFeature
    geojson_layer = dl.GeoJSON(
        data=geojson_data,
        id="geojson",
        hideout={'min_rank': df['rank'].min(), 'max_rank': df['rank'].max()},
        style=style_handle,
        onEachFeature=on_each_feature
    )

    # Return the Map component
    return dl.Map(
        id="map",
        children=[
            dl.TileLayer(),
            geojson_layer  # Add the GeoJSON layer with tooltips to the Map
        ],
        center=[20, 0],
        zoom=2,
        style={'width': '100%', 'height': '100vh'}
    )
