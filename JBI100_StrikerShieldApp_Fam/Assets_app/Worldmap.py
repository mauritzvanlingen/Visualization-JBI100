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

on_each_feature = assign("""function(feature, layer) {
        if (feature.properties && feature.properties.ADMIN) {
            layer.bindTooltip(feature.properties.ADMIN);
        }
    }""")

geojson_layer = dl.GeoJSON(
        data=geojson_data,
        id="geojson",
        hideout={'min_rank': df['rank'].min(), 'max_rank': df['rank'].max()},
        style=style_handle,
        onEachFeature=on_each_feature
    )

def generate_map(map_center=[20, 0],map_zoom=2, marker=None):

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