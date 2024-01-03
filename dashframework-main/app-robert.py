from jbi100_app.main import app
from jbi100_app.views.parallel_charts import ParallelCharts

from dash import html
from dash.dependencies import Input, Output


if __name__ == '__main__':
    
    pc = ParallelCharts(
        color_team_1=[200,0,50],
        color_team_2=[0, 200, 50],
        data_source_path="FIFA DataSet/Data/" # set path to data folder of FIFA dataset
    )
    pc.read_files()
    pc.preprocess_data()

    app.layout = html.Div(
        id="app-container",
        children=[
            # Left column
            html.Div(
                id="left-column",
                className="three columns",
                children=pc.menu_layout()
            ),

            # Right column
            html.Div(
                id="right-column",
                className="nine columns",
                children=pc.figures(['data_set_main'], 'Argentina', 'France')[1] #default
            ),
        ],
    )

    # If graph is selected, then graph is added and the variables of the graphs are added as an option to explanation
    @app.callback(
        [Output('explanation_selection', 'options'), 
         Output('right-column', 'children')],
        [Input('select-team-1', 'value'),
         Input('select-team-2', 'value'),
        Input('graph-dropdown', 'value')]
    )
    def update_graphs(team_1, team_2, selected_graphs):
        if isinstance(selected_graphs, list):
            return pc.figures(selected_graphs, team_1, team_2)
        else:
            return pc.figures([selected_graphs], team_1, team_2)

    # Display explanation of selected variable
    @app.callback(
        [Output('explanation', 'children')],
        [Input('explanation_selection', 'value')]
    )
    def update_explanation(variable):
        if variable:
            return [f"This is the explanation for variable: {variable}"]
        else:
            return ["Choose a variable for which to show the explanation here."]

    app.run_server(debug=False, dev_tools_ui=False)