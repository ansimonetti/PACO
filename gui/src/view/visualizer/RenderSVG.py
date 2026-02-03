from uuid import uuid4
from dash import Output, Input, State, ctx, html, dcc, MATCH
import dash_bootstrap_components as dbc

class RenderSvg:
	def __init__(self, type, index, zoom_min=0.1, zoom_max=2.0, zoom_bar_placement="left", zoom_bar_height=300, default_zoom=1.0):

		self.type = type
		self.index = index

		self.input_store_id = {"type": f"{type}-store", "index": index}
		self.visualizer_id = {"viz_type": f"{type}-content", "index": index}
		self.svg_div_id = {"viz_type": f"{type}-svg", "index": index}
		self.zoom_slider_id = {"viz_type": f"{type}-zoom-slider", "index": index}
		self.zoom_reset_id = {"viz_type": f"{type}-reset-zoom", "index": index}
		self.zoom_in_id = {"viz_type": f"{type}-increase-zoom", "index": index}
		self.zoom_out_id = {"viz_type": f"{type}-decrease-zoom", "index": index}
		self.zoom_settings_id = {"viz_type": f"{type}-zoom-settings", "index": index}

		self.zoom_min = zoom_min
		self.zoom_max = zoom_max
		self.default_zoom = default_zoom

		self.zoom_bar_placement = zoom_bar_placement
		self.zoom_bar_height = zoom_bar_height

	def get_visualizer(self, zoom_bar_placement=True, height=0):
		elements = [
			dcc.Store(id=self.zoom_settings_id, data={"min": self.zoom_min, "max": self.zoom_max, "default": self.default_zoom}),
		]

		svg_style = {"height": "100%", "overflow": "auto"}
		if zoom_bar_placement:
			elements.append(self.get_zoom_bar())
			svg_style["width"] = "100%"

		elements.append(html.Div(id=self.svg_div_id, style=svg_style))

		if height > 0:
			return html.Div(elements, id=self.visualizer_id,
					style={"position": "relative", "height": f"{height}px", "width": "calc(100% - 60px)", "display": "flex",
			"flexDirection": "column", "flex": "1"})


		return html.Div(elements, id=self.visualizer_id, style={"position": "relative", "height": "100%", "width": "100%", "display": "flex",
										 "flexDirection": "column", "flex": "1" })

	def get_zoom_bar(self):
		marks = {
			x: str(x)
			for x in sorted(set(
				[self.zoom_min, self.zoom_max] +
				[round(i * 0.5, 1) for i in range(int(self.zoom_min * 2) + 1, int(self.zoom_max * 2) + 1)]
			))
		}
		return html.Div([
			dbc.Button("+", id=self.zoom_in_id, color="light", size="sm", className="mb-1"),
			dcc.Slider(
				id=self.zoom_slider_id,
				min=self.zoom_min,
				max=self.zoom_max,
				step=0.1,
				value=self.default_zoom,
				included=False,
				vertical=True,
				tooltip={"placement": "right", "always_visible": True},
				updatemode="drag",
				marks=marks
			),
			dbc.Button("−", id=self.zoom_out_id, color="light", size="sm", className="mt-1"),
			dbc.Button("1x", id=self.zoom_reset_id, color="light", size="sm", className="mt-1")
		], style={
			"position": "absolute",
			"bottom": "1rem",
			self.zoom_bar_placement: "1.2rem",
			"height": f"{self.zoom_bar_height}px",
			"display": "flex",
			"flexDirection": "column",
			"alignItems": "center",
			"background": "rgba(255,255,255,0.9)",
			"padding": "0.5rem",
			"borderRadius": "0.5rem",
			"boxShadow": "0 0 5px rgba(0,0,0,0.2)",
			"zIndex": 10
		})

	@staticmethod
	def register_callbacks(callback, type):

		@callback(
			Output({"viz_type": f"{type}-svg", "index": MATCH}, "children"),
			Output({"viz_type": f"{type}-zoom-slider", "index": MATCH}, "value"),
			Input({"type": f"{type}-store", "index": MATCH}, "data"),
			Input({"viz_type": f"{type}-zoom-slider", "index": MATCH}, "value"),
			Input({"viz_type": f"{type}-reset-zoom", "index": MATCH}, "n_clicks"),
			Input({"viz_type": f"{type}-increase-zoom", "index": MATCH}, "n_clicks"),
			Input({"viz_type": f"{type}-decrease-zoom", "index": MATCH}, "n_clicks"),
			State({"viz_type": f"{type}-zoom-settings", "index": MATCH}, "data")
		)
		def render_and_zoom(dot_data, zoom_value, reset_clicks, plus_clicks, minus_clicks, zoom_settings):

			if not dot_data:
				return html.Div(""), 1.0

			if not zoom_settings or "min" not in zoom_settings or "max" not in zoom_settings:
				zoom_min = 0.1
				zoom_max = 2.0
				default_zoom = 1.0
			else:
				zoom_min = zoom_settings["min"]
				zoom_max = zoom_settings["max"]
				default_zoom = zoom_settings.get("default", 1.0)

			svg = dot_data
			triggered = ctx.triggered_id
			zoom = zoom_value or 1.0

			if triggered and isinstance(triggered, dict) and triggered.get("viz_type") == f"{type}-reset-zoom":
				zoom = 1.0
			elif triggered and isinstance(triggered, dict) and triggered.get("viz_type") == f"{type}-increase-zoom":
				zoom = round(min(zoom_max, zoom + 0.1), 1)
			elif triggered and isinstance(triggered, dict) and triggered.get("viz_type") == f"{type}-decrease-zoom":
				zoom = round(max(zoom_min, zoom - 0.1), 1)

			return html.Div([
				html.Div(
					html.ObjectEl(
						data=svg,
						type="image/svg+xml",
						style={
							"width": "100%",
							"height": "100%",
							"transform": f"scale({zoom})",
							"transformOrigin": "0 0",
							"cursor": "grab"
						}
					),
					style={
						"display": "flex",
						"alignItems": "center",
						"justifyContent": "center",
						"height": "100%",
						"width": "100%",
					}
				)
			], key=str(uuid4())), zoom
