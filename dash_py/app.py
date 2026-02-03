from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import dash
app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
            suppress_callback_exceptions=True, 
        )
# https://github.com/PietroSala/process-impact-benchmarks
app.layout = html.Div([        
        dcc.Store(id = 'bpmn-lark-store', data={}),
        dcc.Store(id = 'chat-ai-store'),
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
    app.run(debug=True, host="0.0.0.0", port="8050", dev_tools_hot_reload=False) #run_server()# 127.0.0.1 0.0.0.0 http://157.27.86.122:8050/