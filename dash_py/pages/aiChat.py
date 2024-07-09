import dash
from dash import html, dcc, Input, Output, State, callback


dash.register_page(__name__, path='/ai')

layout = html.Div([
    dcc.Input(id='input-box', type='text', placeholder='Type your message here...'),
    html.Button('Send', id='send-button'),
    html.Div(id='chat-output')
])

@callback(
    Output('chat-output', 'children'),
    [Input('send-button', 'n_clicks')],
    [State('input-box', 'value')],
    prevent_initial_call=True
)
def update_output(n_clicks, value):
    if value:
        response = 'not ai linked' #ollama.chat(model='llama3', messages=[{'role': 'user', 'content': value}])
        return html.Div([
            html.P(f"User: {value}"),
            html.P(f"Assistant: {response['message']['content']}")
        ])
