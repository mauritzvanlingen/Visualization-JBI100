import dash
from dash import dcc, html, Input, Output
import dash_leaflet as dl
from dash_extensions.javascript import assign
import pandas as pd
import json
from JBI100_StrikerShieldApp.Assets_app.Menu_app import make_menu_layout
from JBI100_StrikerShieldApp.Assets_app.Worldmap import generate_map

# Define the style for the hovering menu
menu_style = {
    'position': 'absolute',  # Position it absolutely so it can float over the map
    'top': '10px',  # Adjust the top position to your liking
    'left': '10px',  # Adjust the left position to your liking
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
df = pd.read_csv('json_teamsmapped.csv', delimiter=',')
team_to_country = df.set_index('team')['country'].to_dict()

with open('modified_countries.geojson', 'r') as f:
    geojson_data = json.load(f)

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Overall app layout
app.layout = html.Div(
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
@app.callback(
    Output("geojson", "hideout"),
    [Input('rank-slider', 'value')]
)
def update_geojson_style(selected_range):
    min_rank, max_rank = selected_range
    return {"min_rank": min_rank, "max_rank": max_rank}

@app.callback(
    Output("map", "center"),
    Output("map", "zoom"),
    [Input('dropdown_country', 'value')]
)
def update_map_on_team_select(selected_team):
    default_zoom = 2  # Default zoom level
    default_center = [20, 0]  # Default map center, adjust as needed
    if selected_team is None:
        return default_center, default_zoom
    if selected_team:
        selected_country = team_to_country.get(selected_team)
        if selected_country:
            for feature in geojson_data['features']:
                if feature['properties']['ADMIN'] == selected_country:
                    # Calculate the center of the country
                    # This is a placeholder, you'll need a function to calculate this based on the geometry
                    country_center = calculate_center(feature['geometry'])
                    new_zoom = 5  # Set a new zoom level to zoom in on the country
                    return country_center, new_zoom



def calculate_center(geometry):
    if geometry['type'] == 'Polygon':
        return calculate_polygon_centroid(geometry['coordinates'][0])
    elif geometry['type'] == 'MultiPolygon':
        # For MultiPolygons, calculate the centroid of each polygon and average them
        centroids = [calculate_polygon_centroid(polygon[0]) for polygon in geometry['coordinates']]
        return [sum(x) / len(centroids) for x in zip(*centroids)]
    return [20, 0]  # Default in case of an unsupported geometry type

def calculate_polygon_centroid(coords):
    # Averaging latitude and longitude
    lat = [p[1] for p in coords]
    lon = [p[0] for p in coords]
    centroid_lat = sum(lat) / len(lat)
    centroid_lon = sum(lon) / len(lon)
    return [centroid_lat, centroid_lon]


if __name__ == '__main__':
    app.run_server(debug=True)
