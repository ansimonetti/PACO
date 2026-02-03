import dash_bootstrap_components as dbc

from gui.src.view.syntax.choice import get_choice_layout
from gui.src.view.syntax.loop import get_loop_layout
from gui.src.view.syntax.nature import get_nature_layout
from gui.src.view.syntax.parallel import get_parallel_layout
from gui.src.view.syntax.syntax import get_syntax_layout
from gui.src.view.syntax.tasks import get_tasks_layout


def layout():
    return dbc.Container([
        get_syntax_layout(),
        get_tasks_layout(),
        get_parallel_layout(),
        get_choice_layout(),
        get_nature_layout()#,
        #get_loop_layout()  #TODO Daniel
    ])

#             ## Choices:
#             for each type of gateway, the choices are defined based on who or what takes the decision which are (only for XOR):

#             - `^` : Exclusive gateway
#                 - Person: the decision is taken by a person and no further notetion is needed.
#                     - Example: `Task1 ^ Task2`
#                 - Nature: the decision is taken given a certain probability:
#                     - Example: `Task1 ^ [0.3]Task2 ` --> the probability of choosing Task1 is 0.3 and Task2 is 0.7
#                 - Adversary: the decision is taken by an adversary.
#                      - Example: `Task1 ^ []Task2` --> the adversary will choose for this gateway.            
#             - < ... > : Loop gateway
#                 - Person: the decision is taken by a person and no further notetion is needed.
#                     - Example: `< Task1 >`
#                 - Nature: the decision is taken given a certain probability:
#                     - Example: `< [0.3]Task1 >` --> the probability of choosing Task1 is 0.3 and Task2 is 0.7
#                 - Adversary: the decision is taken by an adversary.
#                      - Example: `< []Task1 >` --> the adversary will choose for this gateway.
            
