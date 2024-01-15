import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
from PIL import Image
from helperFunctionsArlette import list_countries, formation_to_coordinates, calculate_normalized_means, return_df
from dash.exceptions import PreventUpdate


# Initialize the Dash app
app = dash.Dash(__name__)

countries_list = list_countries()

dropdown_options_countries = [{'label': country, 'value': country} for country in countries_list]

dropdown_options_stats = [
    {'label': 'Player positions', 'value': 'positions'},
    {'label': 'Mean number of touches', 'value': 'touches'},
    {'label': 'Mean number of tackles', 'value': 'tackles'},
]

# Create a figure
# img_array = Image.open("jbi100_app/assets/soccer-field.jpg")
# fig = go.Figure(go.Image(z=img_array))

# fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
# fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)

# height = 500
# width = 1000
# h_line = 700
# w_line= 1044

# # Add shapes to the layout of the figure
# fig.update_layout(
#     height=height,  # Set the height of the figure
#     width=width,  # Set the width of the figure
#     margin=dict(l=20, r=20, t=20, b=20),  # Adjust margins to reduce white space
#     paper_bgcolor="rgba(0,0,0,0)",  # Set background color of the figure to transparent
#     plot_bgcolor="rgba(0,0,0,0)",  # Set background color of the plotting area to transparent
# )
    # Initialize the figure with the soccer field image
img_array = Image.open("jbi100_app/assets/soccer-field.jpg")
fig = go.Figure(go.Image(z=img_array))
height = 500
width = 1000
h_line = 700
w_line= 1044
fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)

width_real = 1045
left_half = {
'type': 'rect',
'x0': 0,
'y0': 0,
'x1': width_real / 2,  # x1 is at the halfway point of the width
'y1': h_line,
'line': {'width': 0},  # Invisible border
'fillcolor': 'rgba(0, 0, 255, 0.2)',  # Semi-transparent blue
'opacity': 0  # Start as invisible
}

right_half = {
    'type': 'rect',
    'x0': width_real / 2,
    'y0': 0,
    'x1': width_real,
    'y1': h_line,
    'line': {'width': 0},
    'fillcolor': 'rgba(255, 0, 0, 0.2)',  # Semi-transparent red
    'opacity': 0
}
shapes = [left_half, right_half]
fig.update_layout(
    height=height,  # Set the height of the figure
    width=width,  # Set the width of the figure
    margin=dict(l=20, r=20, t=20, b=20),  # Adjust margins to reduce white space
    paper_bgcolor="rgba(0,0,0,0)",  # Set background color of the figure to transparent
    plot_bgcolor="rgba(0,0,0,0)",  # Set background color of the plotting area to transparent
    shapes = [left_half, right_half]
)

# Dash app layout
app.layout = html.Div(
    children=[
        html.H1("Soccer Strategy Tool", style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='country-dropdown',
            options=dropdown_options_countries,
            value=None  # Default value on load
        ),
       
        html.Div(
            children=[
        html.Div(
            children=[
                dcc.Graph(id='soccer-field', figure=fig)
            ],
            style={'display': 'flex', 'justifyContent': 'center', 'width': '50%'}
        ),
        
        html.Div(id='feature-checkbox-country', style={'display': 'none', 'width': '50%'},
            children=[
            
            html.Div(id='feature-selection-container', children=[
            html.H2("Select a feature"),
            dcc.Dropdown(
                id='feature-dropdown',
                value=None,
            )]),
        
        html.Div(id='checklist-container', 
                 children=[
        html.H2("Check box to include in radarplot"),
        dcc.Checklist(
        id='radar-feature-checklist',
        options=[],  # Options will be populated in the callback
        value=[],  # No default values
        labelStyle={'display': 'block'}  # Display each checkbox in a new line
        ),
        html.Button('Uncheck all', id='reset-button', n_clicks=0)]), 
        
        html.Div(id='opponent-selection-container', children=[
            html.H2("Select a country to compare features"),
            dcc.Dropdown(
                id='opponent-dropdown',
                options=dropdown_options_countries,  # Options will be populated in the callback
                value=None,
            )])            ], 
            )], style={'display': 'flex', 'justifyContent': 'center'}),

        html.Div(
            children=[
        
        html.Div(id='goalkeeper-stats', style={'width': '40%'}),
        # Inside your app.layout
        html.Div([
        dcc.Graph(id='radar-plot')
        ], id='radar-plot-container', style={'display': 'none', 'width': '60%'}),
           ], style={'display': 'flex', 'justifyContent': 'center'})
           ], style={'textAlign': 'center'}        

        )

@app.callback(
    Output('radar-feature-checklist', 'value'),
    [Input('reset-button', 'n_clicks')]
)
def reset_checklist(n_clicks):
    # When the button is clicked, reset the checklist value to an empty list
    return [] if n_clicks > 0 else dash.no_update

@app.callback(
    Output('soccer-field', 'figure'),
    [Input('country-dropdown', 'value'),
     Input('soccer-field', 'hoverData')],
    [State('soccer-field', 'figure')])
def update_figure(selected_country, hoverData, current_figure):
    ctx = dash.callback_context
    img_array = Image.open("jbi100_app/assets/soccer-field.jpg")
    fig = go.Figure(go.Image(z=img_array))
    height = 500
    width = 1000
    h_line = 700
    w_line= 1044
    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_layout(
    height=height,  # Set the height of the figure
    width=width,  # Set the width of the figure
    margin=dict(l=20, r=20, t=20, b=20),  # Adjust margins to reduce white space
    paper_bgcolor="rgba(0,0,0,0)",  # Set background color of the figure to transparent
    plot_bgcolor="rgba(0,0,0,0)",  # Set background color of the plotting area to transparent
    )

    if not ctx.triggered:
        # If no input has been triggered yet, raise PreventUpdate to do nothing
        raise PreventUpdate

    # Get the ID of the input that triggered the callback
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if selected_country != None:
        # Call the function to get positions for the selected country
        positions = formation_to_coordinates(selected_country)
        # Add each player position as a separate trace
        idx_pos = 1
        for pos in positions:
            if idx_pos <= 7:
                fig.add_trace(go.Scatter(
                    x=[pos[0]],  # Multiply by 1.5 if you need to scale the x position
                    y=[pos[1]],
                    mode='markers',
                    name=f'Player at {pos}',
                    marker=dict(size=10, color='black')
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=[pos[0]],  # Multiply by 1.5 if you need to scale the x position
                    y=[pos[1]],
                    mode='markers',
                    name=f'Player at {pos}',
                    marker=dict(size=10, color='black')
                ))
            idx_pos = idx_pos+1

        fig.update_yaxes(range=[0, h_line])
        fig.update_layout(showlegend=False)
        
    if triggered_id == 'soccer-field':
        if hoverData:
            # Check where the hover is and update the opacity accordingly
            hover_x = hoverData['points'][-1]['x']
            if hover_x <= width_real / 2:
                shapes[0]['opacity'] = 0.8  # Left half
                shapes[1]['opacity'] = 0 
            else:
                shapes[0]['opacity'] = 0 
                shapes[1]['opacity'] = 0.8  # Right half
        else:
            shapes[0]['opacity'] = 0  # Left half
            shapes[1]['opacity'] = 0  # Left half

        fig.update_layout(shapes=shapes)

    return fig

@app.callback(Output('goalkeeper-stats', 'children'),
              [Input('soccer-field', 'clickData'), 
               Input('country-dropdown', 'value'),
               Input('feature-dropdown', 'value')])
def display_click_data(clickData, selected_country, selected_feature):
    if clickData is not None:
        width_real = 1045
        point_id = clickData['points'][-1]['x'] # Assuming the point's text is its unique identifier
        
        if point_id <= width_real / 2 and selected_feature is not None:
            df, list_feat = return_df('def')
            fig = go.Figure()
            fig.add_trace(go.Box(y=df[selected_feature], name='Global'))

            # Highlight the selected country's value
            valAnno = df[df['team'] == selected_country][selected_feature].values[0]
            fig.add_trace(go.Scatter(x=['Global'], y=[valAnno], mode='markers', marker=dict(color='red', size=12), name=selected_country))

            # Update layout of the figure
            fig.update_layout(
                #title=f'Boxplot of {selected_feature}',
                xaxis=dict(tickvals=[1], ticktext=['Global']),
                yaxis=dict(title=selected_feature)
            )

            # Return the box plot as part of the layout
            return html.Div([
                #html.H2(f"Metrics of defensive strategy"),
                dcc.Graph(figure=fig)
            ])
        elif point_id > width_real / 2 and selected_feature is not None:

            df, list_feat = return_df('att')
            fig = go.Figure()
            fig.add_trace(go.Box(y=df[selected_feature], name='Global'))

            # Highlight the selected country's value
            valAnno = df[df['team'] == selected_country][selected_feature].values[0]
            fig.add_trace(go.Scatter(x=['Global'], y=[valAnno], mode='markers', marker=dict(color='red', size=12), name=selected_country))

            # Update layout of the figure
            fig.update_layout(
                #title=f'Boxplot of {selected_feature}',
                xaxis=dict(tickvals=[1], ticktext=['Global']),
                yaxis=dict(title=selected_feature)
            )

            # Return the box plot as part of the layout
            return html.Div([
                #html.H2(f"Metrics of attacking strategy"),
                dcc.Graph(figure=fig)
            ])
    return 

@app.callback(
    [Output('feature-dropdown', 'options'),
     Output('feature-dropdown', 'style'),
     Output('feature-checkbox-country', 'style')],
    [Input('soccer-field', 'clickData')],
    [State('country-dropdown', 'value')]
)
def update_feature_dropdown(clickData, selected_country):
    if clickData is not None:
        point_id = clickData['points'][-1]['x']
        width_real = 1045
        if point_id <= width_real / 2:
            df, list_feat = return_df('def')
        else:
            df, list_feat = return_df('att')
        
        options = [{'label': feat, 'value': feat} for feat in list_feat]
        return options, {'display': 'block'}, {'display': 'block'}  # Show the dropdown
    return [], {'display': 'none'}, {'display': 'none'}   # Hide the dropdown

@app.callback(
    [Output('radar-feature-checklist', 'options'),
     Output('checklist-container', 'style')],
    [Input('feature-dropdown', 'value')],
    [State('radar-feature-checklist', 'options')]
)
def update_feature_checklist(selected_feature, existing_options):
    if selected_feature:
        # Check if the option for the selected feature already exists
        if not any(option['value'] == selected_feature for option in existing_options):
            # If it doesn't exist, add a new option for the selected feature
            existing_options.append({'label': selected_feature, 'value': selected_feature})

        # Return the updated options and make the checklist visible
        return existing_options, {'display': 'block'}
    else:
        # If no feature is selected, return the existing options and hide the checklist
        return existing_options, {'display': 'none'}

@app.callback(
    [Output('radar-plot', 'figure'),
     Output('radar-plot-container', 'style')],
    [Input('radar-feature-checklist', 'value'),
     Input('country-dropdown', 'value'),
     Input('opponent-dropdown', 'value')])
def update_radar_plot(selected_features, selected_country, selected_opp):
    if selected_country and selected_features:
        df, _ = return_df('both')
        
        # Filter the DataFrame to only include the selected features for the selected country
        df_selected = df[df['team'] == selected_country][selected_features].dropna()

        # Normalize the values for the radar plot, if necessary
        # This depends on the range of your data and the requirements for your plot
        df_normalized = df_selected/df[selected_features].dropna().mean()
        #df_glob = df[selected_features].dropna().mean()/df[selected_features].dropna().mean()
        if selected_opp == None:
            df_opp = df[selected_features].dropna().mean()/df[selected_features].dropna().mean()
        else:
            df_selected = df[df['team'] == selected_opp][selected_features].dropna()
            df_opp = df_selected/df[selected_features].dropna().mean()

        # Create radar plot
        fig = go.Figure()

        
        fig.add_trace(go.Scatterpolar(
            r=df_opp.values.flatten().tolist(),
            theta=selected_features,
            fill='toself'
        ))

        fig.add_trace(go.Scatterpolar(
            r=df_normalized.values.flatten().tolist(),
            theta=selected_features,
            fill='toself'
        ))      

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True
                )
            ),
            showlegend=False
        )
        
        return fig, {'display': 'block', 'width': '50%', 'padding': '20px'}
    else:
        # Return an empty figure if no country or features are selected
        return go.Figure(), {'display': 'none'}


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)