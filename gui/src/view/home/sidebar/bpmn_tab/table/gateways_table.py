import dash_bootstrap_components as dbc
from dash import html, dcc
from gui.src.env import DELAYS, PROBABILITIES, LOOP_PROBABILITY, LOOP_ROUND


def create_table(columns, rows):
	if len(rows) == 0:
		return html.Div()

	return html.Div([
		dbc.Table(
			[html.Thead(html.Tr([html.Th(col) for col in columns]))] + rows,
			bordered=False,
			hover=True,
			responsive=True,
			striped=True,
			className="table-sm",
			style={
				"width": "auto",
				"margin": "auto",
				"borderCollapse": "collapse"
			}
		)
	], style={
		"padding": "10px",
		"border": "1px solid #ccc",
		"borderRadius": "10px",
		"marginTop": "20px",
		"maxHeight": "500px",
		"overflowY": "auto",
		"display": "block"
	})


def create_choices_table(bpmn_store, choices):
	for name in choices:
		if name not in bpmn_store[DELAYS]:
			bpmn_store[DELAYS][name] = 0

	rows = [
		html.Tr([
			html.Td(name),
			html.Td(dcc.Input(value=bpmn_store[DELAYS][name], type="number", min=0, step=1, debounce=True,
							  id={'type': 'choice-delay', 'index': name}, style={'width': '7ch', "border": "none"}))
		]) for name in choices
	]

	return create_table(["Choices", "Delay"], rows)


def create_natures_table(bpmn_store, natures):
	for name in natures:
		if name not in bpmn_store[PROBABILITIES]:
			bpmn_store[PROBABILITIES][name] = 0.5

	rows = [
		html.Tr([
			html.Td(name),
			html.Td(dcc.Input(value=bpmn_store[PROBABILITIES][name], type="number", min=0, max=1, step=0.001, debounce=True,
							  id={'type': 'nature-prob', 'index': name}, style={'width': '7ch', "border": "none"}))
		]) for name in natures
	]
	return create_table(["Natures", "Probability"], rows)


def create_loops_table(bpmn_store, loops):
	for name in loops:
		if name not in bpmn_store[LOOP_PROBABILITY]:
			bpmn_store[LOOP_PROBABILITY][name] = 0.5
		if name not in bpmn_store[LOOP_ROUND]:
			bpmn_store[LOOP_ROUND][name] = 1

	rows = [
		html.Tr([
			html.Td(name),
			html.Td(dcc.Input(value=bpmn_store[LOOP_PROBABILITY][name], type="number", min=0, max=1, step=0.001, debounce=True,
							  id={'type': 'loop-prob', 'index': name}, style={'width': '7ch', "border": "none"})),
			html.Td(dcc.Input(value=bpmn_store[LOOP_ROUND][name], type="number", min=1, max=100, step=1, debounce=True,
							  id={'type': 'loop-round', 'index': name}, style={'width': '7ch', "border": "none"}))
		]) for name in loops
	]
	return create_table(["Loops", "Probability", "Max Iteration"], rows)
