import os

ALGORITHMS = {  # strategies with labels
    'paco': 'PACO',
}

ALGORITHMS_MISSING_SYNTAX = {
    's1': [],
    's2': [],
    's3': []
}
#### PATHS ##############################
PATH_ASSETS = 'assets/'

BPMN_FOLDER = 'bpmnSvg/'
PATH_IMAGE_BPMN_FOLDER = PATH_ASSETS + BPMN_FOLDER

PATH_BPMN = PATH_ASSETS + 'bpmn'
PATH_PARSE_TREE = PATH_ASSETS + 'parse_tree'

PATH_EXECUTION_TREE = PATH_ASSETS + 'execution_tree'


PATH_EXPLAINER = PATH_ASSETS + 'explainer/'
PATH_EXPLAINER_DECISION_TREE = PATH_EXPLAINER + 'decision_tree'
PATH_BDD = PATH_EXPLAINER + 'bdd'
PATH_STRATEGIES = PATH_ASSETS + 'strategies'

PATH_STRATEGY_TREE = PATH_ASSETS + 'strategy_tree'



### args for tree LARK
EXPRESSION = 'expression'
IMPACTS = 'impacts'
PROBABILITIES = 'probabilities'
DURATIONS = 'durations'
DELAYS = 'delays'
H = 'h'
IMPACTS_NAMES ='impacts_names'
LOOP_ROUND = 'loop_round'
### SYNTAX
LOOP_PROBABILITY = 'loop_probability'
# BPMN RESOLUTION #######################
RESOLUTION = 300
#############################
# STRATEGY 
STRATEGY = 'strategy'
BOUND = 'bound'



# Experiments
BENCHMARKS_DB = 'benchmarks.sqlite'
LOG_FILENAME = 'benchmark_output.log'
TELEGRAM_CONFIG = "src/experiments/telegram/telegram_config.json"


# Logger
import sys

LOG_TO_FILE = "--log-to-file" in sys.argv
LOG_PATH = os.getenv("PACO_LOG_PATH", "logs/paco.log")

