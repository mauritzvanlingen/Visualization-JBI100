# Import necessary libraries
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# Import helper functions from a custom module
from jbi100_app.views.helperFunctionsApp import corr_plots, create_merged_df,  get_cats, get_descriptions, get_labels, getFeatFromLabel

# Initialize the Dash app with a dark theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Get feature categories and columns
feat_cats = get_cats()
feat_columns = []
for category_columns in feat_cats.values():
    feat_columns += category_columns
feat_columns = list(set(feat_columns))

# Create a dictionary for feature descriptions
feature_descriptions = {item: item for item in feat_columns}

# Create a merged DataFrame
df_merge = create_merged_df(feat_columns)
df_merge = df_merge.reset_index()


# Define constants for layout
WIDTH_VIOLIN_PLOTS = 1150

def create_modal():
    """Create a modal window for displaying feature correlations."""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Feature Correlations"), style={"maxWidth": "800px"} ),
            dbc.ModalBody(dcc.Graph(id='imageCorr', figure=[corr_plots('defense', feat_cats, df_merge, ['Argentina', 'Senegal'])], 
                                    style={"maxWidth": "800px"} ))
        ], 
        id="image-modal",
        is_open=False, 
    )

# Define the layout of the app
app.layout = (
    dbc.Container(style={'width': '80%', 'margin': '0 auto',  'font-family': 'verdana'}, fluid=True, children=[create_modal(),
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
                dcc.Dropdown(id='feature_dd', options=[{'label': feat, 'value': feat} for feat in feat_columns], style={'color': 'black'}, multi= True, value=['tackles', 'tackles_won', 'tackles_def_3rd', 'tackles_mid_3rd']),
                html.Hr(className='bg-light'), 
                html.H2('Choose Raw or Min-Max Scaled Data', className='text-white', style={'fontSize': '1.5em'}),
        dbc.Checklist(options=[{"label": "", "value": 1}],value=[],id="normalize-toggle",switch=True,),
    html.Div(id='normalize-label', children='Using Min-Max Scaled Data', className='text-white'),
    html.Hr(className='bg-light'),
        html.H2('Select Countries to Compare', className='text-white', style={'fontSize': '1.5em'}),
         html.Div(id='text3', children='Select countries manually', className='text-white'),
            dcc.Dropdown(id='country-select-dropdown', value=['Argentina', 'Senegal'], options=[{'label': team, 'value': team} for team in sorted(df_merge['team'].unique())], style={'color': 'black'}, multi=True), 
            html.Div(id='text4', children='Or click on a country in the bar chart below', className='text-white')])], color="dark"), width=4),
        dbc.Col(dcc.Graph(id='plot'), id='plot_con', style={'height': '300px'})]),
    html.Br(style={"line-height": "5"}),
    dbc.Row(dcc.Graph(id='bar-chart'), id='bar-chart_con', style={'height': '300px'},),
    html.Div(id='selected-feature-bc', style={'display': 'none'}),
    html.Div(id='selected-data')]))


@app.callback(
    Output('selected-feature-bc', 'children'),
    [Input('plot', 'clickData')],
    [State('feature_dd', 'options')])
def store_clicked_feature(clickData, feature_options):
    """
    Update the selected feature based on click data from the plot.

    Args:
        clickData (dict): Data from the clicked point on the plot.

    Returns:
        The label of the selected feature.
    """
    if clickData is not None:
        # Extract the label of the clicked feature
        label = clickData['points'][0]['x']
        feature_label = getFeatFromLabel(label)
        return feature_label
    else:
        # Prevent update if there's no click data
        raise PreventUpdate


@app.callback(
    [Output("image-modal", "is_open"),
     Output("feature_dd", "value")],
    [Input("open-modal-btn", "n_clicks"),
     Input("imageCorr", "clickData")],
    [State("image-modal", "is_open"),
     State('feature_dd', 'options'),
     State("feature_dd", "value")])
def toggle_modal(n1, clicked, is_open, feature_options, current_value):
    """
    Callback to toggle the modal window and update the value of the feature dropdown.
    The modal window is toggled based on user interactions with the 'open-modal-btn'
    and the feature correlation graph. Additionally, this callback updates the 
    selected features in the dropdown based on the user's click on the correlation graph.

    Args:
        n1 (int): Number of clicks on the open-modal button.
        clicked (dict): Data from the clicked point on the image correlation graph.
        is_open (bool): Current state of the modal (open or closed).
        feature_options (list): List of feature options.
        current_value (list): Current selected values in the feature dropdown.

    Returns:
        tuple: A tuple containing the new state of the modal and the updated feature dropdown value.
    """

    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "open-modal-btn":
        # Toggle the modal open/close state
        return [not is_open, dash.no_update]  
    elif trigger_id == "imageCorr" and clicked:
        # Update the feature dropdown based on the clicked feature
        feat_idx = clicked['points'][0]['curveNumber']
        clicked_feat_label = feature_options[feat_idx]['label']
        clicked_feat_value = getFeatFromLabel(clicked_feat_label)
        if current_value and isinstance(current_value, list):
            if clicked_feat_value not in current_value:
                new_value = current_value + [clicked_feat_value]
            else: 
                new_value = current_value
        else:
            new_value = [clicked_feat_value]
        return [is_open, new_value]
    return [is_open, dash.no_update]


@app.callback(
    [Output("imageCorr", "figure")],
    [Input("btn-1", "n_clicks"), Input("btn-2", "n_clicks"), Input("btn-3", "n_clicks")],
    [State('country-select-dropdown', 'value'),
    State("imageCorr", "figure")])
def update_corrPlots(btn1, btn2, btn3, selected_countries, existing_figure):
    """
    Callback to update the correlation plot based on the category button clicked by the user.
    The plot is updated to reflect correlations for either 'defense', 'possession', or 'attack'
    categories, depending on the button clicked.

    Args:
        btn1 (int): Number of clicks on the 'Defense' button.
        btn2 (int): Number of clicks on the 'Possession' button.
        btn3 (int): Number of clicks on the 'Attack' button.
        existing_figure (dict): The existing figure object of the correlation plot.

    Returns:
        list: A list containing the updated figure object for the correlation plot.
    """
    # Determine which button triggered the callback
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Update the correlation plot based on the clicked button
    if button_id in ["btn-1", "btn-2", "btn-3"]:
        if button_id == "btn-1":
            # Update plot for 'defense' category
            fig = corr_plots('defense', feat_cats, df_merge, selected_countries)
        elif button_id == "btn-2":
            # Update plot for 'possession' category
            fig = corr_plots('possession', feat_cats, df_merge, selected_countries)
        elif button_id == "btn-3":
            # Update plot for 'attack' category
            fig = corr_plots('attack', feat_cats, df_merge, selected_countries)
        return [fig]
    
    # Return the existing figure if no button is clicked
    return [corr_plots('defense', feat_cats, df_merge, selected_countries)]

@app.callback(
    [Output('plot', 'figure'),
     Output('plot', 'style'),
     Output('plot_con', 'style'),
     Output('country-select-dropdown', 'value')],
    [Input('feature_dd', 'value'),
     Input('normalize-toggle', 'value'),
     Input('imageCorr', 'clickData'),
     Input('bar-chart', 'clickData'),
     Input('country-select-dropdown', 'value'),
     Input('imageCorr', 'selectedData')],
     [State('feature_dd', 'options')]
)
def update_violin_plot_with_countries(selected_features, normalize, corrClick, barClick, selected_countries, brushingSelect, feature_options):
    """
    Update the violin plot based on selected features and countries. This callback
    also adjusts the data normalization and handles click events on the bar chart
    to select countries for comparison.

    Args:
        selected_features (list): List of selected features for the violin plot.
        normalize (list): List indicating whether data should be normalized.
        corrClick (dict): Data from click event on the correlation plot.
        barClick (dict): Data from click event on the bar chart.
        selected_countries (list): List of selected countries for comparison.
        feature_options (list): List of feature options.

    Returns:
        tuple: Contains the updated figure for the violin plot, styles for the plot
        and its container, and the updated list of selected countries.
    """
    # Update selected countries based on bar chart clicks

    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if barClick and button_id == 'bar-chart':
        countryClicked = barClick['points'][0]['x']
        if selected_countries is None:
            selected_countries = [countryClicked]
        elif countryClicked not in selected_countries:
            selected_countries.append(countryClicked)
    
    if brushingSelect and button_id == 'imageCorr':
        points = brushingSelect['points']
        countryClicked = [point['text'] for point in points]

        if selected_countries is None:
            selected_countries = countryClicked
        else:
            for country in countryClicked:
                if country not in selected_countries:
                    selected_countries.append(country)
                    
    if len(selected_countries)>12:
        selected_countries = selected_countries[:12]

    # Define color mapping for countries
    cmap = plt.get_cmap('hsv', 13)
    colors = cmap(np.linspace(0, 1, 13))
    hex_colors = [cm.colors.rgb2hex(color) for color in colors]
    print(hex_colors)
    hex_colors = hex_colors[::2] + hex_colors[-1:0:-2]
    print(hex_colors)
    country_colors = {country: hex_colors[i] for i, country in enumerate(selected_countries)}

    # Determine if data should be normalized
    use_normalized_data = not (1 in normalize)
    fig = go.Figure()

    # Handle case when no features are selected
    if not selected_features:
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
                'font': {'size': 28}}])
    else:
        # Create violin plot for each selected feature
        for feature in selected_features:
            data = df_merge[feature]
            # Normalize data if required
            if use_normalized_data:
                min_val = data.min()
                max_val = data.max()
                data = (data - min_val) / (max_val - min_val)
                ytitle = 'Min-max scaled values'
            else:
                ytitle = 'Raw values per 90 minutes'

            fig.add_trace(go.Violin(
                y=data,
                name=get_labels(feature),
                line_color='black',
                fillcolor='white',
                box_visible=True,
                meanline_visible=True,
                showlegend=False
            ))
            desc = get_descriptions(feature)
            fig.add_annotation(
                x=get_labels(feature), y=-0.08, xref='x', yref='paper', text="&#9432;",
                showarrow=False, font=dict(size=16, color="black"),
                hovertext=desc,
                hoverlabel=dict(bgcolor="white", font_size=20, font_family="Arial"))
        
        # Add data points for selected countries
        if selected_countries:
            country_legend_added = {country: False for country in selected_countries}
            for country in selected_countries:
                country_color = country_colors.get(country)
                for feature in selected_features:
                    country_data = df_merge[df_merge['team'] == country][feature]
                    if use_normalized_data:
                        country_data = (country_data - df_merge[feature].min()) / (df_merge[feature].max() - df_merge[feature].min())
                    showlegend = not country_legend_added[country]
                    fig.add_trace(go.Scatter(
                        x=[get_labels(feature)] * len(country_data),
                        y=country_data,
                        mode='markers',
                        marker=dict(color=country_color, size=10),
                        name=country if showlegend else '',
                        legendgroup=country,
                        showlegend=showlegend
                    ))
                    country_legend_added[country] = True

        # Update layout of the violin plot
        fig.update_layout(
            title_text='Click on violin plot to visualise feature values in bar chart',
            yaxis_title=ytitle,
            showlegend=True,
            margin=dict(l=10, r=10, t=50, b=60),
            height=600,
            width=WIDTH_VIOLIN_PLOTS,)

    return fig, {'display': 'block'}, {'display': 'block', 'width': '10%'}, selected_countries


@app.callback(
    Output('normalize-label', 'children'),
    [Input('normalize-toggle', 'value')])
def update_normalize_label(normalize):
    """
    Callback to update the label indicating whether the data is being displayed in raw form
    or normalized. The label changes based on the state of the normalization toggle.

    Args:
        normalize (list): List indicating whether data should be normalized.

    Returns:
        str: A string indicating the current data display mode (raw or normalized).
    """
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
    """
    Callback to update the styles of category buttons based on which button was clicked.
    Highlights the clicked button and updates the options in the feature dropdown
    according to the selected category.

    Args:
        btn1 (int): Number of clicks on the 'Defense' button.
        btn2 (int): Number of clicks on the 'Possession' button.
        btn3 (int): Number of clicks on the 'Attack' button.

    Returns:
        tuple: Contains updated styles for the category buttons and the updated options for the feature dropdown.
    """
    ctx = dash.callback_context
    # Check if the callback was triggered by any of the buttons
    if not ctx.triggered:
        # Default to 'defense' category if no button is clicked
        list_feat = feat_cats["defense"]
        options = [{'label': get_labels(feat), 'value': feat} for feat in list_feat]
        return [{'background-color': 'darkgreen'}, {}, {}, options]
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        # Define styles for the selected and default states of the buttons
        selected_style = {'background-color': 'darkgreen'}
        default_style = {}

        # Update styles and dropdown options based on the clicked button
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
    Output("bar-chart", "figure"),
    [Input('selected-feature-bc', 'children'),
     Input('normalize-toggle', 'value'),
     Input('country-select-dropdown', 'value')])
def update_bar_chart(feat, normalize, countries):
    """
    Callback to update the bar chart based on the selected feature and normalization state.
    Displays a bar chart of the selected feature for each team, with an option to
    normalize the data.

    Args:
        feat (str): The selected feature to display in the bar chart.
        normalize (list): List indicating whether data should be normalized.

    Returns:
        go.Figure: A Plotly graph object figure for the updated bar chart.
    """
    # Determine if data should be normalized
    use_normalized_data = not (1 in normalize)

    # Use 'points' as the default feature if none is selected
    if not feat:
        feat = "points"

    # Prepare the data for the bar chart
    df_temp = df_merge[['team', feat]].sort_values(by=feat)
    data = df_temp[feat]

    # Normalize data if required
    if use_normalized_data:
        min_val = data.min()
        max_val = data.max()
        data = (data - min_val) / (max_val - min_val)
        ytitle = 'Min-max scaled values'
        df_temp[feat] = data
    else:
        ytitle = 'Raw values per 90 minutes'

    cmap = plt.get_cmap('hsv', 13)
    colors = cmap(np.linspace(0, 1, 13))
    hex_colors = [cm.colors.rgb2hex(color) for color in colors]
    country_colors = {country: hex_colors[i] for i, country in enumerate(countries)}

    # Create and configure the bar chart
    fig = go.Figure()
    for i, team in df_temp.iterrows():
        color = country_colors.get(team['team']) if team['team'] in countries else 'grey'
        fig.add_trace(go.Bar(x=[team['team']], y=[team[feat]], name=team['team'], marker_color=color, showlegend=False))
    fig.update_layout(
        #title_text=get_labels(feat),
        xaxis={'categoryorder': 'total descending'},
        yaxis_title = get_labels(feat),
        margin=dict(l=30, r=10, t=10, b=10)
    )
    
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)





