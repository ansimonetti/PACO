import dash_bootstrap_components as dbc
from dash import html


def get_new_impact_button():
	return html.Div([
		dbc.Input(
			id={'type': 'impact-name-input', 'index': 'main'},
			placeholder='New impact',
			debounce=True,
			style={'flexGrow': 1, 'marginRight': '4px'}
		),
		dbc.Button(
			"+",
			id={'type': 'add-impact-button', 'index': 'main'},
			n_clicks=0,
			color="success",
			size="sm",
			style={"padding": "0.25rem 0.4rem", "lineHeight": "1"}
		),
	], style={'width': '100%', 'display': 'flex', 'alignItems': 'center'})
