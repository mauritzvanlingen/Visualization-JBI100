import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
from helperFunctionsArletteV2 import corr_plots, create_merged_df, figure_pa, get_cats
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

df_merge = create_merged_df()
df_merge = df_merge.reset_index()
feat_cats = get_cats()
feat_columns = []
for category_columns in feat_cats.values():
        feat_columns += category_columns

selected_country ='Argentina'
selected_opp = 'Senegal'
matchesNr1 = 10
matchesNr2 = 20
glob_select = ['France', 'Ecuador', 'Engeland', 'Croatia', 'Morocco']
default_check = ["average_shot_distance", "blocked_passes", "aerials_won_pct", "errors"]
rank_low = 1
rank_high = 5

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
    dbc.Col(html.Div([
        html.Span("●", className='text-danger', style={'fontSize': '1.5em'}),
        html.Span(f"{selected_country}: ", className='text-light'),
        html.Span(f"Data from {matchesNr1} matches", className='text-light'), 
    ], className='text-center py-2')),
    
    dbc.Col(html.Div([
        html.Span("●", className='text-primary', style={'fontSize': '1.5em'}),
        html.Span(f"{selected_opp}: ", className='text-light'),
        html.Span(f"Data from {matchesNr2} matches", className='text-light'), 
    ], className='text-center py-2')),], className='my-1', justify='center', style={'marginTop': '5px'}),

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
                html.H2('Compare Feature', className='text-white', style={'fontSize': '1.5em'}),
                dcc.Dropdown(id='feature_dd', options=[{'label': feat, 'value': feat} for feat in feat_columns], style={'color': 'black'}, value='blocked_passes'),
            ])
        ], color="dark"), width=4),
        dbc.Col(dcc.Graph(id='plot'), id='plot_con'),
    ]),

    dbc.Row([
        dbc.Col(html.Div(style={'height': '40px'}))]),

    dbc.Row([
            
            dbc.Col(dbc.Card([
            dbc.CardHeader(html.H2("Summarize", className='text-white', style={'fontSize': '1.5em'})),
            dbc.CardBody([
                dcc.Checklist(
                    id='pa-feature-checklist',
                    options=[{'label': feat, 'value': feat} for feat in default_check],
                    value=default_check,
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
     Input('feature_dd', 'value')])
def update_pa_plot(selected_features, dropdownFeature):
    if dropdownFeature and selected_features:
        fig = figure_pa(selected_features, selected_country, selected_opp)  
        fig.update_layout(
            font=dict(size=14),
            margin=dict(l=75, r=75, t=50, b=20)
        ) 
        return fig, {'height': '220px', 'width':'800px'}, {'display': 'block'}
    else:
        return go.Figure(), {}, {'display': 'none'}

@app.callback(
    Output('pa-feature-checklist', 'value'),
    [Input('reset-button', 'n_clicks')])
def reset_checklist(n_clicks):
    return [] if n_clicks > 0 else dash.no_update

@app.callback(
    [Output('pa-feature-checklist', 'options'),
     Output('pa-feature-checklist', 'labelStyle')],
    [Input('feature_dd', 'value')],
    [State('pa-feature-checklist', 'options')])
def update_feature_checklist(selected_feature, existing_options):
    if selected_feature:
        if not any(option['value'] == selected_feature for option in existing_options):
            existing_options.append({'label': selected_feature, 'value': selected_feature})
        return existing_options, {'display': 'block'}
    else:
        return existing_options, {'display': 'none'}

@app.callback(
    [Output('plot', 'figure'),
     Output('plot', 'style'),
     Output('plot_con', 'style')],
    [Input('feature_dd', 'value'),]
)
def update_plot(selected_feature):
    if selected_feature:
        fig = go.Figure()
        fig.add_trace(go.Box(y=df_merge[selected_feature], name='Global', marker=dict(color='darkgreen', size=12)))
        df_globSel = df_merge[df_merge['team'].isin(glob_select)]
        fig.add_trace(go.Box(y=df_globSel[selected_feature], name=(f'Countries with FIFA ranking {rank_low}-{rank_high}'), marker=dict(color='purple', size=12)))
        valAnno = df_merge[df_merge['team'] == selected_country][selected_feature].values[0]
        fig.add_trace(go.Scatter(x=['Country'], y=[valAnno], mode='markers', marker=dict(color='red', size=12), name=selected_country))
        valAnno = df_merge[df_merge['team'] == selected_opp][selected_feature].values[0]
        fig.add_trace(go.Scatter(x=['Country'], y=[valAnno], mode='markers', marker=dict(color='blue', size=12), name=selected_opp))
        fig.update_layout(showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10))
        return fig, {'height': '300px', 'width':'800px'}, {'display': 'block'}
    else:
        return go.Figure(), {}, {'display': 'none'}
    
            
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
    app.run_server(debug=True)





