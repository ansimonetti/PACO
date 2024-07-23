from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import dash
app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

app.layout = html.Div([
        html.H1('BPMN+CPI APP!', style={'textAlign': 'center'}),
        dbc.DropdownMenu([
            dbc.DropdownMenuItem(
                f"{page['name']}", href=page["relative_path"]
            ) for page in dash.page_registry.values()                
            ],
            label="Menu",
        ),
        dash.page_container,
    ], style={'padding':'30px'})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8050", dev_tools_hot_reload=False) #run_server()#