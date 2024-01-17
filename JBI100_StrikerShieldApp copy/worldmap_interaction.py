import dash
from dash import dcc, html, Input, Output
import dash_leaflet as dl
from dash_extensions.javascript import assign
import pandas as pd
import json
import time

style_handle = assign("""function(feature, context){
    const {min_rank, max_rank} = context.hideout;
    const rank = feature.properties.rank;
    if(rank >= min_rank && rank <= max_rank){
        return {fillColor: 'red', color: 'grey', weight: 0.5};
    }
    return {fillColor: 'grey', color: 'grey', weight: 0.5};
}""")


# Load the modified GeoJSON data
df = pd.read_csv('JBI100_StrikerShieldApp/json_teamsmapped.csv', delimiter=',')

with open('JBI100_StrikerShieldApp/modified_countries.geojson', 'r') as f:
    geojson_data = json.load(f)

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    dl.Map(
        children=[
            dl.TileLayer(),
            dl.GeoJSON(data=geojson_data,
                       id="geojson",
                       hideout={'min_rank': df['rank'].min(),
                                'max_rank': df['rank'].max()},
                       style=style_handle),
        ],
        center=[20, 0],
        zoom=2,
        style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}
    ),
    html.Div(id='country-name-display', style={'marginTop': '20px', 'fontSize': '20px'}),
    dcc.RangeSlider(
        id='rank-slider',
        min=df['rank'].min(),
        max=df['rank'].max(),
        step=1,
        marks={i: str(i) for i in range(df['rank'].min(), df['rank'].max() + 1,10)},
        value=[df['rank'].min(), df['rank'].max()],
        tooltip={"placement": "bottom", "always_visible": True}

    )
])
@app.callback(
    Output('country-name-display', 'children'),
    [Input('geojson', 'click_feature')]
)
def country_click(feature):
    if feature is not None:
        # Assuming 'name' is the property that holds the English name of the country
        country_name = feature['properties'].get('ADMIN', 'No name found')
        return f'Country selected: {country_name}'
    return 'Click on a country'

@app.callback(
    Output("geojson", "hideout"),
    [Input('rank-slider', 'value')]
)
def update_geojson_style(selected_range):
    min_rank, max_rank = selected_range
    # Return the updated range to the hideout property
    return {"min_rank": min_rank, "max_rank": max_rank}

if __name__ == '__main__':
    app.run_server(debug=True)
