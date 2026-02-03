import os

from lark import Lark, ParseTree

APP_NAME = "PACO GUI"

def _normalize_base_url(value: str | None, default: str) -> str:
    if not value:
        return default
    url = value.strip()
    if not url:
        return default
    return url if url.endswith("/") else f"{url}/"


def _get_env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


_API_PORT = _get_env_int("PACO_API_PORT", 8000)
_SIMULATOR_PORT = _get_env_int("SIMULATOR_API_PORT", 8001)

URL_SERVER = _normalize_base_url(os.getenv("PACO_API_URL"), f"http://127.0.0.1:{_API_PORT}/")
SIMULATOR_SERVER = _normalize_base_url(
    os.getenv("PACO_SIMULATOR_URL"),
    f"http://127.0.0.1:{_SIMULATOR_PORT}/",
)
GUI_HOST = os.getenv("PACO_GUI_HOST", "0.0.0.0")
GUI_PORT = _get_env_int("PACO_GUI_PORT", 8050)
HEADERS = {"Content-Type": "application/json"}

DB_PATH = 'bpmn_cpi.sqlite'

###############
# MODEL
###############
MODEL = "lmstudio-community/Llama-3.1-Nemotron-70B-Instruct-HF-GGUF/Llama-3.1-Nemotron-70B-Instruct-HF-Q4_K_M.gguf"
MODEL_1 = "lmstudio-community/Llama-3.1-Nemotron-70B-Instruct-HF-GGUF"
MODEL_2 = "lmstudio-community/Llama-3.1-Nemotron-70B-Instruct-HF-GGUF/Llama-3.1-Nemotron-70B-Instruct-HF-Q4_K_M.gguf:2"

LM_STUDIO_MODEL = (os.getenv("LM_STUDIO_MODEL") or "openai/gpt-oss-20b").strip()
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-4o-mini").strip()
ANTHROPIC_MODEL = (os.getenv("ANTHROPIC_MODEL") or "claude-3-5-sonnet-20241022").strip()
GEMINI_MODEL = (os.getenv("GEMINI_MODEL") or "gemini-2.5-flash-lite").strip()
OPENROUTER_MODEL = (os.getenv("OPENROUTER_MODEL") or "openai/gpt-4o-mini").strip()

LLM_PROVIDER_OPTIONS = [
    {"label": "LM Studio (local)", "value": "lmstudio"},
    {"label": "OpenAI", "value": "openai"},
    {"label": "OpenRouter", "value": "openrouter"},
    {"label": "Claude", "value": "anthropic"},
    {"label": "Gemini", "value": "gemini"},
]
LLM_DEFAULT_PROVIDER = "lmstudio"
LLM_MODELS_BY_PROVIDER = {
    "lmstudio": [LM_STUDIO_MODEL, MODEL, MODEL_1, MODEL_2],
    "openai": [OPENAI_MODEL],
    "openrouter": [OPENROUTER_MODEL],
    "anthropic": [ANTHROPIC_MODEL, "claude-3.5-opus"],
    "gemini": ["gemini-2.5-flash-lite", GEMINI_MODEL, "gemini-2.5-flash"],
}
LLM_MODEL_OPTIONS_BY_PROVIDER = {
    provider: [{"label": model, "value": model} for model in models]
    for provider, models in LLM_MODELS_BY_PROVIDER.items()
}
LLM_DEFAULT_MODEL_BY_PROVIDER = {
    provider: models[0] for provider, models in LLM_MODELS_BY_PROVIDER.items() if models
}


###############
# GRAMMAR
###############
sese_diagram_grammar = r"""
?start: xor

?xor: parallel
    | xor "/" "[" NAME "]" parallel -> choice
    | xor "^" "[" NAME "]" parallel -> natural

?parallel: sequential
    | parallel "||" sequential  -> parallel

?sequential: region
    | sequential "," region -> sequential    

?region: 
    | NAME   -> task
    | "<" xor ">" -> loop
    | "<" "[" NAME "]"  xor ">" -> loop_probability
    | "(" xor ")"

%import common.CNAME -> NAME
%import common.NUMBER
%import common.WS_INLINE

%ignore WS_INLINE
"""
SESE_PARSER = Lark(sese_diagram_grammar, parser='lalr')

### args for tree LARK
EXPRESSION = 'expression'
IMPACTS = 'impacts'
NAMES = 'names'
PROBABILITIES = 'probabilities'
DURATIONS = 'durations'
DELAYS = 'delays'
H = 'h'
IMPACTS_NAMES ='impacts_names'
LOOP_ROUND = 'loop_round'
LOOP_PROBABILITY = 'loop_probability'

# STRATEGY 
STRATEGY = 'strategy'
BOUND = 'bound'



#############################
# PATHS
#############################

PATH_ASSETS = 'assets/'
BPMN_FOLDER = 'bpmnSvg/'
PATH_IMAGE_BPMN_FOLDER = PATH_ASSETS + BPMN_FOLDER
PATH_BPMN = PATH_ASSETS + 'bpmn'

PATH_BPMN = PATH_ASSETS + 'bpmn'
PATH_PARSE_TREE = PATH_ASSETS + 'parse_tree'

PATH_EXECUTION_TREE = PATH_ASSETS + 'execution_tree/'
PATH_EXECUTION_TREE_STATE = PATH_EXECUTION_TREE + 'state'
PATH_EXECUTION_TREE_STATE_TIME = PATH_EXECUTION_TREE + 'state_time'
PATH_EXECUTION_TREE_STATE_TIME_EXTENDED = PATH_EXECUTION_TREE + 'state_time_extended'

PATH_EXECUTION_TREE_TIME = PATH_EXECUTION_TREE + 'time'

PATH_EXPLAINER = PATH_ASSETS + 'explainer/'
PATH_EXPLAINER_DECISION_TREE = PATH_EXPLAINER + 'decision_tree'
PATH_EXPLAINER_BDD = PATH_EXPLAINER + 'bdd'
PATH_STRATEGIES = PATH_ASSETS + 'strategies'

PATH_STRATEGY_TREE = PATH_ASSETS + 'strategy_tree/'
PATH_STRATEGY_TREE_STATE = PATH_STRATEGY_TREE + 'state'
PATH_STRATEGY_TREE_STATE_TIME = PATH_STRATEGY_TREE + 'state_time'
PATH_STRATEGY_TREE_STATE_TIME_EXTENDED = PATH_STRATEGY_TREE + 'state_time_extended'
PATH_STRATEGY_TREE_TIME = PATH_STRATEGY_TREE + 'time'

#############################
# ALGORITHMS
#############################
ALGORITHMS = {  # strategies with labels
    's1': 'PACO',
    #'s2': 'Strategy 2',
    #'s3': 'Strategy 3'
}



def extract_nodes(lark_tree: ParseTree) -> (list, list, list, list):
    tasks, choices, natures, loops = extract_nodes_set(lark_tree)
    return list(tasks), list(choices), list(natures), list(loops)

def extract_nodes_set(lark_tree: ParseTree) -> (set, set, set, set):
    tasks, choices, natures, loops = set(), set(), set(), set()
    left_task, left_choices, left_natures, left_loops = set(), set(), set(), set()
    right_task, right_choices, right_natures, right_loops = set(), set(), set(), set()

    def add_unique(s: set, value: str, label: str):
        if value in s:
            raise ValueError(f"Duplicate {label} detected: {value}")
        s.add(value)

    if lark_tree.data == 'task':
        value = lark_tree.children[0].value
        return {value}, set(), set(), set()

    if lark_tree.data in {'choice', 'natural'}:
        if lark_tree.data == 'choice':
            add_unique(choices, lark_tree.children[1].value, "choice")
        else:
            add_unique(natures, lark_tree.children[1].value, "nature")

        left_task, left_choices, left_natures, left_loops = extract_nodes_set(lark_tree.children[0])
        right_task, right_choices, right_natures, right_loops = extract_nodes_set(lark_tree.children[2])

    elif lark_tree.data in {'sequential', 'parallel'}:
        left_task, left_choices, left_natures, left_loops = extract_nodes_set(lark_tree.children[0])
        right_task, right_choices, right_natures, right_loops = extract_nodes_set(lark_tree.children[1])
    elif lark_tree.data == 'loop':
        left_task, left_choices, left_natures, left_loops = extract_nodes_set(lark_tree.children[0])
        right_task, right_choices, right_natures, right_loops = set(), set(), set(), set()
    elif lark_tree.data == 'loop_probability':
        add_unique(loops, lark_tree.children[0].value, "loop")
        left_task, left_choices, left_natures, left_loops = set(), set(), set(), set()
        right_task, right_choices, right_natures, right_loops = extract_nodes_set(lark_tree.children[1])

    for val in left_task.union(right_task):
        add_unique(tasks, val, "task")
    for val in left_choices.union(right_choices):
        add_unique(choices, val, "choice")
    for val in left_natures.union(right_natures):
        add_unique(natures, val, "nature")
    for val in left_loops.union(right_loops):
        add_unique(loops, val, "loop")

    return tasks, choices, natures, loops
