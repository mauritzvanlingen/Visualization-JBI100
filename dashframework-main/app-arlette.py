import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from PIL import Image

# Initialize the Dash app
app = dash.Dash(__name__)

dropdown_options_countries = [
    {'label': 'Country 1', 'value': 'country1'},
    {'label': 'Country 2', 'value': 'country2'},
    # Add more countries as needed
]
dropdown_options_stats = [
    {'label': 'Player positions', 'value': 'positions'},
    {'label': 'Mean number of touches', 'value': 'touches'},
    {'label': 'Mean number of tackles', 'value': 'tackles'},
]

# Create a figure
img_array = Image.open("jbi100_app/assets/soccer-field.jpg")
fig = go.Figure(go.Image(z=img_array))

fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)

height = 500
width = 1000
h_line = 700
w_line= 1044
# Update layout properties to set the figure size and remove white space around the figure
fig.update_layout(
    height=height,  # Set the height of the figure
    width=width,  # Set the width of the figure
    margin=dict(l=20, r=20, t=20, b=20),  # Adjust margins to reduce white space
    paper_bgcolor="rgba(0,0,0,0)",  # Set background color of the figure to transparent
    plot_bgcolor="rgba(0,0,0,0)"  # Set background color of the plotting area to transparent
)

# Dash app layout
app.layout = html.Div(
    children=[
        html.H1("Soccer Strategy Tool", style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='country-dropdown',
            options=dropdown_options_countries,
            value='country1'  # Default value on load
        ),
        dcc.Dropdown(
            id='stats-dropdown',
            options=dropdown_options_stats,
            value='positions'  # Default value on load
        ),
        html.Div(
            children=[
                dcc.Graph(id='soccer-field', figure=fig)
            ],
            style={'display': 'flex', 'justifyContent': 'center'}
        ),
        html.Div(id='goalkeeper-stats')
    ],
    style={'textAlign': 'center'}
)

@app.callback(
    Output('goalkeeper-stats', 'children'),
    [Input('soccer-field', 'clickData')])
def display_click_data(clickData):
    if clickData is not None:
        point_id = clickData['points'][0]['text']  # Assuming the point's text is its unique identifier
        if point_id == 1:
            # Load the goalkeeper's statistics and create a new figure or HTML components to display them
            # For example, let's say you have a DataFrame 'goalkeeper_stats_df'
            return html.Div([
                html.H2("Goalkeeper Statistics"),
                # Create components to display statistics
                # dcc.Graph(figure=goalkeeper_stats_figure) for a new figure
                # Or display raw data
                # html.P(f"Save Percentage: {goalkeeper_stats_df['save_percentage'][0]}")
            ])
    return 


@app.callback(
    Output('soccer-field', 'figure'),
    [Input('country-dropdown', 'value'),
     Input('stats-dropdown', 'value')])
def update_figure(selected_country, selected_statistic):

    # Initialize the figure with the soccer field image
    img_array = Image.open("jbi100_app/assets/soccer-field.jpg")
    fig = go.Figure(go.Image(z=img_array))
    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_layout(
        height=500,
        width=1000,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    if selected_statistic == 'positions':
        df = pd.read_csv(f'{selected_country}_positions.csv')
        fig.add_trace(go.Scatter(
            x=df['x']*1.5,
            y=df['y'],
            mode='markers',
            text=df['player'],
            name='players',
            marker=dict(size=20, color='red')
        ))

    elif selected_statistic == 'touches':
        for third in [1/3, 2/3]:
            fig.add_shape(type="line", x0=third *w_line, y0=0, x1=third * w_line, y1=h_line, line=dict(color="black", width=2, dash="dash"))
        df_touches = pd.DataFrame({
            'Third': ['Defensive 1/3', 'Middle 1/3', 'Attacking 1/3'],
            'Touches': [250, 344, 600]
        })
        third_width = w_line / 3
        for index, row in df_touches.iterrows():
            fig.add_trace(go.Bar(
                x=[(index + 0.5) * third_width],  # Position the bar in the middle of the third
                y=[row['Touches']],
                width=[0.8 * third_width],  # Set the width of the bar to be less than the third's width
                marker_color='blue',
                opacity=0.6,
                name=row['Third']
            ))
        fig.update_yaxes(range=[0, h_line])
        fig.update_layout(showlegend=False)

    elif selected_statistic == 'tackles':
        for third in [1/3, 2/3]:
            fig.add_shape(type="line", x0=third *w_line, y0=0, x1=third * w_line, y1=h_line, line=dict(color="black", width=2, dash="dash"))
        df_tackles = pd.DataFrame({
            'Third': ['Defensive 1/3', 'Middle 1/3', 'Attacking 1/3'],
            'Tackles': [100, 400, 300]
        })
        third_width = w_line / 3
        for index, row in df_tackles.iterrows():
            fig.add_trace(go.Bar(
                x=[(index + 0.5) * third_width],  # Position the bar in the middle of the third
                y=[row['Tackles']],
                width=[0.8 * third_width],  # Set the width of the bar to be less than the third's width
                marker_color='red',
                opacity=0.6,
                name=row['Third']
            ))
        fig.update_yaxes(range=[0, h_line])
        fig.update_layout(showlegend=False)

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)