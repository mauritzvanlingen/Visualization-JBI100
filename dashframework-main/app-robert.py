from jbi100_app.main import app
from jbi100_app.views.parallel_charts import ParallelCharts

from dash import html
from dash.dependencies import Input, Output


if __name__ == '__main__':
    
    pc = ParallelCharts()
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
                children=pc.figures(['data_set_main'], 'Argentina', 'France')
            ),
        ],
    )

    @app.callback(
        Output('right-column', 'children'),
        [Input('select-team-1', 'value'),
         Input('select-team-2', 'value'),
        Input('graph-dropdown', 'value')]
    )
    def update_graphs(team_1, team_2, selected_graphs):
        return pc.figures(selected_graphs, team_1, team_2)


    app.run_server(debug=False, dev_tools_ui=False)