import dash_bootstrap_components as dbc
from dash import html, dcc
from dash_iconify import DashIconify


def get_control():
	return dbc.Card([
		dbc.CardHeader(html.H5('Control Panel')),
		dbc.CardBody([
			dbc.Row([
				dbc.Col(
					dbc.ButtonGroup([
						dbc.Button(DashIconify(icon="lucide:skip-back", width=24), id="btn-back", color="secondary"),
						# dbc.Button(DashIconify(icon="lucide:play", width=24), id="btn-play", color="success"),
						# dbc.Button(DashIconify(icon="lucide:pause", width=24), id="btn-pause", color="warning"),
						# dbc.Button(DashIconify(icon="lucide:stop-circle", width=24), id="btn-stop", color="danger"),
						dbc.Button(DashIconify(icon="lucide:skip-forward", width=24), id="btn-forward", color="secondary"),
					]), width="auto"
				),
				dbc.Col([
					html.Label("Time", style={"marginRight": "10px", "marginBottom": "0", "lineHeight": "38px"}),
					dbc.Input(
						id="time-input",
						type="number",
						min=0.1,
						value=1.0,
						step=0.1,
						style={"width": "80px", "display": "inline-block", "verticalAlign": "middle"}
					)
				], width="auto", className="d-flex align-items-center")
			], className="mt-2")
		])
	], className="mb-3", style={"minWidth": "370px", "width": "100%"})

