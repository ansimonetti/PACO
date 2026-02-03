from dash import html, dcc
from gui.src.view.visualizer.RenderSVG import RenderSvg


def get_bdds_visualizer(choice, type_strategy, svg):
	if type_strategy == "FORCED_DECISION":
		return html.Div(
			html.Iframe(
				src=svg,
				style={"width": "100%", "height": "100%", "border": "none"}
			),
			style={
					"height": "180px",
					"border": "1px solid #eee"
				}
		)

	visualizer = RenderSvg(
		type="bdd",
		index=choice,
		zoom_bar_placement="right",
		zoom_bar_height=300,
		zoom_max=3.0
	)

	return html.Div([
			dcc.Store(id={"type": "bdd-store", "index": choice}, data=svg),
			html.Div(
				visualizer.get_visualizer(zoom_bar_placement=False, height=350),
			),
			visualizer.get_zoom_bar(),
		],
		style={"height": "auto", "maxHeight": "500px", "minHeight": "350px", "width": "100%", "overflow": "auto"}
	)
