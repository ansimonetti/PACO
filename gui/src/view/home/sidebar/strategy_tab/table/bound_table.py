import dash_bootstrap_components as dbc
from dash import html, dcc
from gui.src.env import BOUND


def get_bound_table(bound_store, sorted_impacts_names):
	bounds = {
		name: float(bound_store.get(BOUND, {}).get(name, 1.0))
		for name in sorted_impacts_names
	}

	header = html.Tr([
		html.Th(html.Div([
			html.Span(name, style={
				"whiteSpace": "nowrap",
				"overflow": "hidden",
				"textOverflow": "ellipsis",
				"maxWidth": "80px",
				"display": "inline-block"
			})
		], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-between'}))
		for name in sorted_impacts_names
	])

	row = html.Tr([
		html.Td(dcc.Input(
			value=bounds[name],
			type="number",
			debounce=True,
			style={'width': '80px', "border": "none", "padding": "0.4rem"},
			id={'type': 'bound-input', 'index': name}
		)) for name in sorted_impacts_names
	])

	return html.Div([
		dbc.Table(
			children=[html.Thead(header), html.Tbody([row])],
			bordered=True,
			striped=True,
			responsive=True,
			className="table-sm",
			style={"width": "auto", "margin": "auto", "borderCollapse": "collapse"}
		)
	], style={
		"display": "inline-block",
		"padding": "10px",
		"border": "1px solid #ccc",
		"borderRadius": "10px",
		"marginTop": "20px"
	})
