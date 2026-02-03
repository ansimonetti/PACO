from dash import html, dcc


def get_input_bar():
	return html.Div([
		dcc.Textarea(
			id='chat-input',
			placeholder='Type your message...',
			style={
				'minHeight': '50px',
				'width': '75%',
				'display': 'inline-block',
				'padding': '10px',
				'borderRadius': '5px',
				'border': '1px solid #ccc',
				'marginRight': '10px'
			},
		),
		html.Button(
			'Send',
			id='chat-send-btn',
			n_clicks=0,
			disabled=False,
			style={
				'padding': '10px 20px',
				'borderRadius': '5px',
				'backgroundColor': '#007bff',
				'color': 'white',
				'border': 'none',
				'cursor': 'pointer',
				'opacity': '1'
			}
		)
	], style={'marginTop': '20px'})
