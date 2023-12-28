from jbi100_app.main import app
from jbi100_app.views.menu import make_menu_layout
import pandas as pd
from dash import html, dcc, Output, Input, State
import plotly.express as px

"""
Load sample data, still need to decide what datasets we want to use.
Need to figure out in what folder to put the data and make this path nicer.
change path to your own path where the data is stored for now
"""
df_player_keepers = pd.read_csv(r"C:\Users\Beheerder\Documents\DSAI master\Q2 Courses\Vizualisation\dashframework-main\dashframework-main\Data\FIFA World Cup 2022 Player Data\player_keepers.csv", delimiter=',')
df_keepers_adv = pd.read_csv(r"C:\Users\Beheerder\Documents\DSAI master\Q2 Courses\Vizualisation\dashframework-main\dashframework-main\Data\FIFA World Cup 2022 Player Data\player_keepersadv.csv", delimiter=',')

#data cleaning and normalization
#  - some variables like age do not work yet. 
#####


# Create correlation matrix for the initial dataset
correlation_matrix = df_player_keepers.corr()

# Create heatmap with Plotly Express
fig = px.imshow(correlation_matrix,
                labels=dict(color="Correlation"),
                x=correlation_matrix.columns,
                y=correlation_matrix.index,
                color_continuous_scale="Viridis")

# Customize the layout
fig.update_layout(title='Correlation Heatmap',
                  width=800, height=600,
                  xaxis=dict(title='Features'),
                  yaxis=dict(title='Features'))

app.layout = html.Div(
    id="app-container",
    children=[
        # Right column
        html.Div(
            id="right-column",
            className="nine columns",
            children=[
                # Label for Selected Dataset
                html.Label("Selected Dataset:"),
                # Radio button for selecting dataset
                dcc.RadioItems(
                    id='dataset-radio',
                    options=[
                        {'label': 'Player Keepers', 'value': 'player_keepers'},
                        {'label': 'Keepers Adv', 'value': 'keepers_adv'}
                    ],
                    value='player_keepers',
                    labelStyle={'display': 'block'}
                ),
                # Label for Variables of Interest
                html.Label("Variables of Interest:"),
                # Dropdown for selecting variables
                dcc.Dropdown(
                    id='variable-dropdown',
                    multi=True,
                    value=[],
                    style={'width': '50%'}
                ),
                # Label for Color Palette
                html.Label("Color Palette:"),
                # Dropdown for selecting color palette
                dcc.Dropdown(
                    id='color-scale-dropdown',
                    options=[
                        {'label': 'Viridis', 'value': 'Viridis'},
                        {'label': 'Plasma', 'value': 'Plasma'},
                        {'label': 'Inferno', 'value': 'Inferno'},
                        # Add more color scales as needed
                    ],
                    value='Viridis',
                    style={'width': '50%'},
                    placeholder='Select Color Palette'
                ),
                # Update Plot button
                html.Button(id='update-plot-button', n_clicks=0, children='Update Plot'),
                # Heatmap figure
                dcc.Graph(id='correlation-heatmap', figure=fig)
            ],
        ),
    ],
)

# Define callback to update variables based on selected dataset
@app.callback(
    [Output('variable-dropdown', 'options'),
     Output('variable-dropdown', 'value')],
    [Input('dataset-radio', 'value')]
)
def update_variables(selected_dataset):
    # Choose the appropriate dataset based on the user's selection
    if selected_dataset == 'player_keepers':
        available_variables = df_player_keepers.columns
    elif selected_dataset == 'keepers_adv':
        available_variables = df_keepers_adv.columns
    else:
        available_variables = []

    options = [{'label': col, 'value': col} for col in available_variables]
    value = []  # Clear the currently selected variables when the dataset changes

    return options, value

# Define callback to update heatmap based on selected dataset, variables, and color scale
@app.callback(
    Output('correlation-heatmap', 'figure'),
    [Input('dataset-radio', 'value'),
     Input('update-plot-button', 'n_clicks')],
    [State('variable-dropdown', 'value'),
     State('color-scale-dropdown', 'value')]
)
def update_heatmap(selected_dataset, n_clicks, selected_vars, selected_color_scale):
    # Check if the button was clicked
    if n_clicks == 0:
        return fig  # Return the initial heatmap

    # Choose the appropriate dataset based on the user's selection
    if selected_dataset == 'player_keepers':
        selected_df = df_player_keepers
    elif selected_dataset == 'keepers_adv':
        selected_df = df_keepers_adv
    else:
        selected_df = pd.DataFrame()  # Use an empty DataFrame for an unknown dataset

    # Filter selected variables
    selected_df = selected_df[selected_vars]

    try:
        # Compute correlation matrix for the selected dataset
        correlation_matrix = selected_df.corr()

        # Create updated heatmap with Plotly Express
        updated_fig = px.imshow(correlation_matrix,
                                labels=dict(color="Correlation"),
                                x=correlation_matrix.columns,
                                y=correlation_matrix.index,
                                color_continuous_scale=selected_color_scale)

        # Customize the layout
        updated_fig.update_layout(title=f'Correlation Heatmap - {selected_dataset.capitalize()}',
                                  width=800, height=600,
                                  xaxis=dict(title='Features'),
                                  yaxis=dict(title='Features'))

        return updated_fig

    except Exception as e:
        return fig  # Return the initial heatmap in case of an error

if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_ui=False)
