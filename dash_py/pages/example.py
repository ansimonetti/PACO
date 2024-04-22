import time
import dash
from dash import html, dcc
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
    dcc.Markdown('''
        # Example of a BPMN+CPI
            The BPMN diagram (shonw in figure) depicts a metal manufacturing process that involves cutting, milling,
            bending, polishing, depositioning, and painting a metal piece. 
                 
            The diagram in our syntax will be written as: (Cutting, ( (Bending, (HP ^ [N1]LP ) ) || ( Milling, ( FD / [C1] RD))), (HPHS / [C2] LPLS))
            The associated impacts are: {"Cutting": {"cost": 10, "working_hours": 1}, "Bending":{"cost": 20, "working_hours": 1}, "Milling":{"cost": 50, "working_hours": 1},"HP":{"cost": 5, "working_hours": 4},"LP":{"cost": 5, "working_hours": 1}, "FD":{"cost": 30, "working_hours": 1}, "RD":{"cost": 10, "working_hours": 1}, "HPHS":{"cost": 40, "working_hours": 1}, "LPLS":{"cost": 20, "working_hours": 3}}
            
    '''),
    dbc.Alert(" Remember to put the () brackets around the regions to enhance  readability and secure the parsing. ", color='info'),
    html.Img(src='assets/examples/bpmn_example.png', id='img-bpmn' , style={'height': '200', 'width': '400'}),
    html.H3("BPMN+CPI printed using Lark syntax"),
    html.Img(src='assets/examples/lark_bpmn.svg', id='img-bpmn' , style={'height': '200', 'width': '400'}),
    dcc.Markdown('''            
            The diagram consists of a single-entry-single-exit (SESE) region, with a choice, a probabilistic split, and an impact for each task. The goal is
            to find a strategy that has the overall impact of the process in the limit of the expected impact. Here we explain the process in more details and next we will see which path brings us to the winning strategy.
            The bracketed numbers next to each activity represent impact vectors [a, b] where a = cost of the task and b = hours/men required to complete the task. For instance, cutting the metal piece has the cost
            of 10 units (e.g., currency, resource, etc.), and requires 1 unit of time or manpower (e.g., 1 hour or 1 worker). The numbers next to decision points indicate the probability of each path being chosen. For
            example, there’s a high probability (0.8) of the process moving from bending to light polishing and a low probability (0.2) of it moving to fine heavy polishing.
            Imagine in this example our expected impact is 𝑒𝑖 = [155, 7.5] and we have to find a strategy that guarantees the overall impact of the process does not exceed the expected impact. A strategy (𝑆) is a
            winning one for a BPMN+CPI and a vector bound (𝑒𝑖) if and only if ∑ 𝑝(𝑐)𝐼(𝑐) ≤ 𝑒𝑖 with (𝑐) being the final computation. here we consider two different probable strategies examples that we can choose.
            **Losing strategy example**: after cutting the metal piece we have two tasks after the parallel split node, so we do the bending and milling in parallel. then after milling we have two options to choose from, here
            we choose fine deposition. after bending we have two options to choose from, we choose light polishing with the probability of 0.8. 
            Then, we have two final task to choose from that we select LPLS painting.
            Finally, we have 𝐼 = [115, 11] ∗ 0.2 + [135, 8] ∗ 0.8 = [131, 8.6] > 𝑒𝑖, so by exceeding the 𝑒𝑖 this strategy fails to keep the overall impact below the expected impact.

            **Wining strategy example**: after cutting we perform milling in parallel with bending. we have two options that comes after milling, we choose fine deposition. we have two options to choose after bending,
            we choose light polishing with the probability of 0.8. then we have two final task to choose from that we select HPHS painting this time. finally we have 𝐼 = [135, 9] ∗ 0.2 + [155, 6] ∗ 0.8 = [151, 6.6] < 𝑒𝑖, so
            this strategy successfully kept the overall impact below the expected impact. 
    '''),
])