import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
from helperFunctionsArletteV2 import corr_plots, create_merged_df,  get_cats #, figure_pa
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from jbi100_app.views.parallel_charts_adapted import ViolinPlots
import plotly.express as px

violin_data = pd.read_csv(r"C:\Users\Beheerder\Documents\DSAI master\Q2 Courses\Vizualisation\Visualization-JBI100\data-used.csv")
vp = ViolinPlots(path=r"C:\Users\Beheerder\Documents\DSAI master\Q2 Courses\Vizualisation\Visualization-JBI100\data-used.csv")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

df_merge = create_merged_df()
df_merge = df_merge.reset_index()
feat_cats = get_cats()
feat_columns = []
for category_columns in feat_cats.values():
        feat_columns += category_columns


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

app.layout = dbc.Container(style={'width': '80%', 'margin': '0 auto',  'font-family': 'verdana'}, fluid=True, children=[
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
                dcc.Dropdown(id='feature_dd', options=[{'label': feat, 'value': feat} for feat in feat_columns], style={'color': 'black'}, value='blocked_passes', multi= True), 
                html.H2('Select Countries', className='text-white', style={'fontSize': '1.5em'}),
                
            dcc.Dropdown(
            id='country-select-dropdown',
            options=[{'label': country, 'value': country} for country in df_merge['team'].unique()],
            multi=True,  # Allows multiple selections
            style={'color': 'black', 'background-color': 'white'}
        ), html.H2('Normalize Data', className='text-white', style={'fontSize': '1.5em'}),
dbc.Checklist(
    options=[
        {"label": "Normalize", "value": 1}
    ],
    value=[],
    id="normalize-toggle",
    switch=True,
)
            ])
        ], color="dark"), width=4),
        dbc.Col(dcc.Graph(id='plot'), id='plot_con'),
    ]),

    dbc.Row([
        dbc.Col([
            html.Label('Select Country', className='text-white'),
            dcc.Dropdown(
    id='country-dropdown',
    options=[{'label': country, 'value': country} for country in df_merge['team'].unique()],
    value=[],
    multi=True,  # Allows multiple selections
    style={'color': 'black', 'background-color': 'white'}  # Set text color to black and dropdown background to white
)

        ], width=6)
    ]),

    dbc.Row([
            
            dbc.Col(dbc.Card([
            dbc.CardHeader(html.H2("Summarize", className='text-white', style={'fontSize': '1.5em'})),
            dbc.CardBody([
                dcc.Checklist(
                    id='pa-feature-checklist',
                    options=[{'label': col, 'value': col} for col in violin_data.columns],
                    value=[],
                    labelStyle={'display': 'block', 'color': '#fff'}
                ),
                dbc.Button('Remove all', id='reset-button', color="warning", n_clicks=0)
            ])
        ], color="dark"), width=4),
        dbc.Col(dcc.Graph(id='pa-plot'), id='pa-plot-container')
        
    ])
])

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
    [Output('pa-plot', 'figure'),
     Output('pa-plot', 'style'),
     Output('pa-plot-container', 'style')],
    [Input('pa-feature-checklist', 'value'),
     Input('country-dropdown', 'value')])
def update_pa_plot(selected_features, selected_countries):
    if not selected_features or not selected_countries:
        # If no feature or country is selected, do not update the plot
        raise PreventUpdate

    # Filter the dataframe for the selected countries
    filtered_data = violin_data[violin_data['team'].isin(selected_countries)]

    # Create dimensions for each selected feature with the range set to [0, 1]
    dimensions = [
        {
            'label': feature,
            'values': filtered_data[feature],
            'range': [0, 1]  # Set the range from 0 to 1 for each feature
        } for feature in selected_features
    ]

    # Create the parallel coordinates plot
    fig = go.Figure(data=go.Parcoords(
        line=dict(color=filtered_data['team'].astype('category').cat.codes, colorscale='Viridis'),
        dimensions=dimensions,
        
        
        
    ))

    # Update layout properties
    fig.update_layout(
    title_text='Parallel Coordinates Plot for Selected Features and Countries',
    margin=dict(l=50, r=50, t=50, b=50),
    
    font=dict(size=12),
    paper_bgcolor='white',  # Change paper background color to white
    plot_bgcolor='white',   # Change plot background color to white
    font_color='black'      # Ensure the font color is black for readability
)


    return [fig, {'display': 'block'}, {'display': 'block', 'width': '100%'}]
# Define a color dictionary outside of the callback
country_colors = {country: color for country, color in zip(df_merge['team'].unique(), px.colors.qualitative.Plotly)}


@app.callback(
    [Output('plot', 'figure'),
     Output('plot', 'style'),
     Output('plot_con', 'style')],
    [Input('feature_dd', 'value'),
     Input('country-select-dropdown', 'value'),
     Input('normalize-toggle', 'value')]
)
def update_violin_plot_with_countries(selected_features, selected_countries, normalize):
    # Normalize data if toggle is on
    normalize_data = 1 in normalize

    if not isinstance(selected_features, list):
        selected_features = [selected_features]

    fig = go.Figure()

    for feature in selected_features:
        if feature in df_merge.columns:
            data = df_merge[feature]
            if normalize_data:
                # Normalize data by centering around 0
                mean = data.mean()
                normalized_data = data - mean
            else:
                normalized_data = data

            fig.add_trace(go.Violin(
                y=normalized_data,
                name=feature,
                line_color='black',
                fillcolor='grey',
                box_visible=True,
                meanline_visible=True
            ))

    # Add markers for the selected countries for each feature, if any countries are selected
    if selected_countries:
        for country in selected_countries:
            country_color = country_colors.get(country, 'black')
            for feature in selected_features:
                country_data = df_merge[df_merge['team'] == country]
                if feature in country_data.columns:
                    data = country_data[feature]
                    if normalize_data:
                        # Normalize the country-specific data in the same way as the violin plots
                        data = data - df_merge[feature].mean()

                    fig.add_trace(go.Scatter(
                        x=[feature] * len(country_data),
                        y=data,
                        mode='markers',
                        marker=dict(color=country_color, size=10),
                        name=f"{country} - {feature}"
                    ))

    fig.update_layout(
        title_text='Violin Plots for Selected Features and Countries',
        showlegend=True,
        margin=dict(l=10, r=10, t=50, b=10),  # Increase top margin to fit the title
        height=450,  # Increase the height of the plot
        width=950   # Increase the width of the plot
    )

    return fig, {'height': '300px', 'width': '800px'}, {'display': 'block'}

@app.callback(
    [Output('btn-1', 'style'),
     Output('btn-2', 'style'),
     Output('btn-3', 'style'),
     Output('feature_dd', 'options')],
    [Input('btn-1', 'n_clicks'),
     Input('btn-2', 'n_clicks'),
     Input('btn-3', 'n_clicks')]
)
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

if __name__ == '__main__':
    app.run_server(debug=True, port = 8000)





