import json
import dash
import dash_bootstrap_components as dbc
from gui.src.example_registry import EXAMPLE_PATHS
from gui.src.view.example.first_example.layout import get_first_example
from gui.src.controller.example.render import register_example_callbacks, render_example
from gui.src.view.example.second_example import get_second_example
from gui.src.view.example.third_example import get_third_example
from gui.src.view.example.fourth_example import get_fourth_example

FIRST_EXAMPLE_KEY = "fig8"
SECOND_EXAMPLE_KEY = "unavoidable"
THIRD_EXAMPLE_KEY = "random"
FOURTH_EXAMPLE_KEY = "harbor"

FIRST_EXAMPLE_PATH = EXAMPLE_PATHS[FIRST_EXAMPLE_KEY]
SECOND_EXAMPLE_PATH = EXAMPLE_PATHS[SECOND_EXAMPLE_KEY]  # TODO DECISON BASED EXAMPLE
THIRD_EXAMPLE_PATH = EXAMPLE_PATHS[THIRD_EXAMPLE_KEY]
FOURTH_EXAMPLE_PATH = EXAMPLE_PATHS[FOURTH_EXAMPLE_KEY]
def layout():
    with open(FIRST_EXAMPLE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)
    bpmn, bpmn_svg_base64 = render_example(data)

    with open(SECOND_EXAMPLE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)
    bpmn2, bpmn_svg_base64_2 = render_example(data)

    with open(THIRD_EXAMPLE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)
    bpmn3, bpmn_svg_base64_3 = render_example(data)

    with open(FOURTH_EXAMPLE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)
    bpmn4, bpmn_svg_base64_4 = render_example(data)

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                get_first_example("bpmn-example", bpmn, bpmn_svg_base64, example_key=FIRST_EXAMPLE_KEY)
            ], width=12)
        ], class_name="mb-4"),
        dbc.Row([
            dbc.Col([
                get_second_example("bpmn-example2", bpmn2, bpmn_svg_base64_2, example_key=SECOND_EXAMPLE_KEY)
            ], width=12)
        ], class_name="mb-4"),
        dbc.Row([
            dbc.Col([
                get_third_example("bpmn-example3", bpmn3, bpmn_svg_base64_3, example_key=THIRD_EXAMPLE_KEY)
            ], width=12)
        ], class_name="mb-4"),
        dbc.Row([
            dbc.Col([
                get_fourth_example("bpmn-example4", bpmn4, bpmn_svg_base64_4, example_key=FOURTH_EXAMPLE_KEY)
            ], width=12)
        ], class_name="mb-4")
    ], fluid=True)


register_example_callbacks(dash.callback, id="bpmn-example", example_path=FIRST_EXAMPLE_PATH)
register_example_callbacks(dash.callback, id="bpmn-example2", example_path=SECOND_EXAMPLE_PATH)
register_example_callbacks(dash.callback, id="bpmn-example3", example_path=THIRD_EXAMPLE_PATH)
register_example_callbacks(dash.callback, id="bpmn-example4", example_path=FOURTH_EXAMPLE_PATH)
