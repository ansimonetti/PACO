from dash import html


def get_header():
	return html.Div([
		html.H5("Chat with your AI", style={'margin': 0}),
		html.Button(
			'Delete',
			id='chat-clear-btn',
			n_clicks=0,
			disabled=False,
			style={
				'marginLeft': 'auto',
				'padding': '6px 12px',
				'borderRadius': '5px',
				'backgroundColor': '#dc3545',
				'color': 'white',
				'border': 'none',
				'cursor': 'pointer',
				'opacity': '1'
			}
		)
	], style={
		'display': 'flex',
		'justifyContent': 'space-between',
		'alignItems': 'center',
		'marginBottom': '15px'
	})
