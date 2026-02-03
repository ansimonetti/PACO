import dash_bootstrap_components as dbc
from dash import html, dcc

from gui.src.env import EXPRESSION, IMPACTS_NAMES
from gui.src.view.visualizer.RenderSVG import RenderSvg


def get_description(bpmn, text_description, warning=False, impacts=False):
	elements = [
		html.P(text_description, style={"marginBottom": "15px"}),
		dcc.Markdown("The expression of the diagram in our syntax will be written as:", style={"marginBottom": "5px"}),
		dcc.Textarea(
			value=bpmn[EXPRESSION],
			readOnly=True,
			style={
				"width": "100%",
				"marginBottom": "15px",
				"whiteSpace": "pre-wrap"
			}
		),
	]
	if warning:
		elements.append(
			dbc.Alert(" Remember to put the () brackets around the regions to enhance readability and secure the parsing. ", color='info'),
		)
	if impacts:
		elements.append(
			html.P(f'''Each task has the following impacts: {', '.join(bpmn[IMPACTS_NAMES])}.''', style={"marginBottom": "15px"})
		)

	return dbc.Card([
		dbc.CardHeader("Description"),
		dbc.CardBody(elements)
	])


def get_render_example(bpmn_dot, id, zoom_min=0.1, zoom_max=3.5):
	id = id + "-svg"
	bpmn_visualizer = RenderSvg(type=id, index="main", zoom_min=zoom_min, zoom_max=zoom_max)
	return [
		dcc.Store(
			id={"type": id + "-store", "index": "main"},
			data=bpmn_dot,
			storage_type='session'
		),
		dbc.Card([
			dbc.CardHeader("Visualization"),
			dbc.CardBody([
				html.Div(
					bpmn_visualizer.get_visualizer(),
					style={"height": "100%", "width": "100%", "overflow": "auto", "marginBottom": "20px", "marginTop": "20px"}
				)
			])
		], style={"height": "100%", "width": "100%"}),
	]



def get_download_layout(id, text_description, example_key=None):
	buttons = []
	# if example_key:
	# 	buttons.append(
	# 		dcc.Link(
	# 			dbc.Button("Try this example", color="success", className="me-2"),
	# 			href=f"/?example={example_key}",
	# 			style={"textDecoration": "none"}
	# 		)
	# 	)
	buttons.append(dbc.Button("Download BPMN JSON", id=id + "-btn"))

	return dbc.Card([
		dbc.CardHeader("Try it yourself!"),
		dbc.CardBody([
			html.P(text_description),
			html.Div(buttons, className="d-flex flex-wrap gap-2"),
			dcc.Download(id=id)
		])
	])
