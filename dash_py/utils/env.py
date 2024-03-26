from lark import Lark

"""
    Defining the grammar for SESE diagrams and useful global variables
"""
sese_diagram_grammar = r"""
?start: xor

?xor: parallel
    | xor "^" parallel -> xor
    | xor "^" "[" NAME "]" parallel -> xor_probability

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
MAX_DELAY = 1

FAILED = False
ADMITTED = True

COMPLETE = 1
CHAR_ACCEPTED = 0
INVALID_CHAR = -1

ALGORITHMS = {  # strategies with labels
    's1': 'PACO', 
    's2': 'Strategy 2', 
    's3': 'Strategy 3'
}

ALL_SYNTAX = ['^', '||', '<', '>', '[]', ',', ''] # all syntax available xor, parallel, loop, adversary
ALGORITHMS_MISSING_SYNTAX = { 
    's2': ['<', '>', '||',], # NO LOOP and parallel
    's3': ['||', '<', '>', '[]', ',', ''] # ONLY XOR
}
#### PATHS ##############################
PATH_IMAGE_BPMN_LARK = 'assets/d.png'
PATH_AUTOMATON = 'assets/automaton.dot'
PATH_AUTOMATON_CLEANED = 'assets/automaton_cleaned.dot'
### args for tree LARK
TASK_SEQ = 'expression'
IMPACTS = 'impacts'
NAMES = 'names'
PROBABILITIES = 'probabilities'
LOOP_THRESHOLD = 'loop_threshold'
DURATIONS = 'durations'
DELAYS = 'delays'
H = 'h'

# 
AUTOMATON_TYPE = 'mealy'
### SYNTAX
LOOPS = 'loops'
ADVERSARIES = 'adversaries'
