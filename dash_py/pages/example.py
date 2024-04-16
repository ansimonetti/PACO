import time
import dash
from dash import html, dcc, Input, Output,State, callback
import dash_bootstrap_components as dbc

import pandas as pd
import plotly.express as px

from utils import check_syntax as cs
from utils import automa as at
from utils.env import ALGORITHMS, TASK_SEQ, IMPACTS, H, DURATIONS, PROBABILITIES, NAMES, DELAYS
from utils.print_sese_diagram import print_sese_diagram
#from solver.tree_lib import print_sese_custom_tree

dash.register_page(__name__, path='/example')

layout = html.Div([
    html.P('This is the  page where an example is provided (Cutting, ( (Bending, (HP ^ [N1]LP ) ) || ( Milling, ( FD / [C1] RD))), (HPHS / [C2] LPLS))'),
])