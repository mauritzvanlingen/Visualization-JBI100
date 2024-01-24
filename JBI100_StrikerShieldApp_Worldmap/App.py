import dash
from dash import dcc, html, Input, Output
import dash_leaflet as dl
from dash_extensions.javascript import assign
import pandas as pd
import json
from JBI100_StrikerShieldApp.Assets_app.Menu_app import make_menu_layout
from JBI100_StrikerShieldApp.Assets_app.Worldmap import generate_map, calculate_center,geojson_layer

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
df = pd.read_csv('../Data/dataset_teams.csv', delimiter=',')
team_to_country = df.set_index('team')['country'].to_dict()

with open('../Data/modified_countries2.geojson', 'r') as f:
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
    Output('stored_team', 'data'),  # Update the stored data
    Input('dropdown_own_team', 'value')  # Listen to the dropdown's value
)
def update_stored_team(selected_team):
    if selected_team:
        return {'team': selected_team}


@app.callback(
    [Output("map", "center"),
     Output("map", "zoom"),
     Output("map", "children")],  # Update this to change the map's children
    [Input('dropdown_opponent', 'value')]
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
