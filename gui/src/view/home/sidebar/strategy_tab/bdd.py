from dash import html
import dash_bootstrap_components as dbc
from gui.src.view.home.sidebar.strategy_tab.bdd_visualizer import get_bdds_visualizer

def get_bdds(bdds: dict):
	cards = []

	for choice in sorted(bdds.keys()):
		type_strategy, svg = bdds[choice]

		visualizer = get_bdds_visualizer(choice, type_strategy, svg)

		label = type_strategy.replace("_", " ").title()

		maxWidth = 500
		if type_strategy == "FORCED_DECISION":
			maxWidth = 160

		card = dbc.Card(
			[
				dbc.CardHeader(
					html.Div([
						html.H5(choice, className="mb-0", style={"marginRight": "10px"}),
						html.P(f"Type: {label}", className="text-body mb-0")
					],
						style={
							"display": "flex",
							"justifyContent": "space-between",
							"alignItems": "center",
							"flexWrap": "wrap"  # così se serve vanno su due righe
						})
				),
				dbc.CardBody(visualizer)
			],
			style={
				"maxWidth": f"{maxWidth}px",
				"width": "100%",
				"marginBottom": "1rem"
			}
		)

		cards.append(card)

	return html.Div(
		cards,
		style={
			"display": "flex",
			"flexWrap": "wrap",
			"gap": "15px",
			"justifyContent": "flex-start",
			"alignItems": "flex-start",
			"width": "100%"
		}
	)
