from dash import html
from gui.src.view.home.sidebar.strategy_tab.bdd import get_bdds
from gui.src.view.home.sidebar.strategy_tab.table.create_advance_table import render_table
import dash_bootstrap_components as dbc

def strategy_results(result: str, expected_impacts: list, guaranteed_bounds: list, possible_min_solution: list, bdds: dict, sorted_impact_names: list, sort_by=None, sort_order="asc"):
	cards = []

	cards.append(
		dbc.Card([
			dbc.CardHeader("Result"),
			dbc.CardBody(html.P(result, className="text-body"))
		], className="mb-3", style={"maxWidth": "370px", "width": "100%"})
	)

	if expected_impacts:
		cards.append(
			dbc.Card([
				dbc.CardHeader("Expected Impacts"),
				dbc.CardBody(
					render_table(sorted_impact_names, [expected_impacts], table="expected")
				)
			], className="mb-3", style={"minWidth": "300px", "maxWidth": "500px", "width": "100%"})
		)

		if bdds:
			cards.append(
				dbc.Card([
					dbc.CardHeader("Explainers"),
					dbc.CardBody([
						html.P("1 is dashed line of BPMN", className="text-body"),
						get_bdds(bdds)
					])
				], className="mb-3", style={"width": "100%"})
			)

	elif guaranteed_bounds:
		cards.append(
			dbc.Card([
				dbc.CardHeader("Guaranteed Bounds"),
				dbc.CardBody(
					html.Div(
						render_table(
							sorted_impact_names,
							guaranteed_bounds,
							include_button=True,
							button_prefix="selected_bound",
							sort_by=sort_by,
							sort_order=sort_order,
							table="guaranteed"
						),
						id="guaranteed-table"
					)
				)
			], className="mb-3", style={"minWidth": "300px", "maxWidth": "500px", "width": "100%"})
		)

	if possible_min_solution:
		cards.append(
			dbc.Card([
				dbc.CardHeader("Possible Min Bounds"),
				dbc.CardBody(
					html.Div(
						render_table(
							sorted_impact_names,
							possible_min_solution,
							include_button=True,
							button_prefix="selected_bound",
							sort_by=sort_by,
							sort_order=sort_order,
							table="possible_min"
						),
						id="possible_min-table"
					)
				)
			], className="mb-3", style={"minWidth": "300px", "maxWidth": "500px", "width": "100%"})
		)

	return html.Div(
		dbc.Container(
			dbc.Row(
				dbc.Col(
					html.Div(
						cards,
						style={
							"display": "flex",
							"flexWrap": "wrap",
							"gap": "15px",
							"justifyContent": "flex-start",
							"alignItems": "flex-start",
							"width": "100%"
						}
					),
					width=12
				)
			),
			fluid=True,
			className="p-3"
		),
		className="sidebar-box"
	)
