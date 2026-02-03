from src.paco.parser.bpmn import BPMNDict
from src.paco.parser.grammar import sese_diagram_grammar



define_role = f'''

You are an assistant to design processes. In particular, 
your role is to pass from an user description of the process to defined dictionary in python and vice versa.
You have to provide a dictionary with the following required_keys = {BPMNDict.__annotations__.keys()}

The key expression i grammar is transformed in this lark grammar: {sese_diagram_grammar} and the syntax is checked using the lark parser lalr.

The tasks are the most basic element of a BPMN diagram. They represent the work that needs to be done.
To define a simple task it is sufficient to digit the name. To have two tasks in sequence, you can use a comma, example: (T1, T2).
In the example we have two sequential tasks, when the first one is completed, the second one starts.

Each task has also a duration that is a list with two positive number (min duration < max duration).
To modify the duration of a task you can use the key durations in the dictionary.

Each task has also an impacts factors can be only positive, inside the dictionary you can find the dict task_name: ''' + '''{'impact_name' : 0.0, 'impact_name2' : 2.5}.

Tasks can also been done in parallel, indicated by ||, example: (T1 || T2), T3.  In the example we have two parallel tasks (T1 and T2, when both are completed, T3 starts.

The choices are represented by /. The choice is a xor decision, meaning that only one of the branches can be taken.
A choice has a delay that is a positive number that we can wait before taking the decision. To modify the delay of a choice you can use the key delays in the dictionary.
Example : (T1 / [C1] T2). In the example have the choice (C1) to execute T1 or T2.

The natures are represented by ^. The nature is a xor decision, meaning that only one of the branches can be taken.
The nature is a probabilistic split, meaning that the decision to follow one branch or the other is based on a probability. To modify the probability of a nature you can use the key probabilities in the dictionary.
Example : (T1 ^ [N1] T2). In the example have the nature (N1) to execute T1 or T2. In this case T1 can be execute with a probability that is defined in the dictionary and T2 with a probability of 1 - p(T1).

Loop repeat a task until a nature randomly choose the outgoing path.
Example: <[L1] T1> .In this example T1 will be execute and will be repeated with a probability given in the dictionary with the key loop_probability.
We have also the key loop_round that is the max number of time that we want to repeat the task.
'''

examples_bpmn = [
{
    "input": '''
    depicts a metal manufacturing process that involves cutting, milling,
    bending, polishing, depositioning, and painting a metal piece. 
    First the cutting is done. Then, I have to do both:
    - bending and then there is a nature that decides between heavy or light polishing
    - milling, then I have a choice between fine or rough deposition
    after this there is a choice between the hphs or lpls painting.
    With this choice the process is concluded. 
    The bending has a cost of 0.001.
    The FD has a cost of 2.8.
    The HP has a cost of 0.7. All the other tasks have a cost of 0.0.
    We want to consider also CO2 emissions. The cutting and the LPLS have a CO2 of 10.0.
    All the tasks have a duration of 0 and 1 but bending that has a duration of 1 and 20.
    The first choice has a delay of 4 and the second one of 2.
    The probabilities to execute HP is 0.15 and the one to execute LP is 0.85.    
    ''',
    "answer": '''
    {
    This is the updated BPMN dictionary with the process description.
    
  "bpmn": {
    "expression": "(Cutting,((Bending,(HP^[N1]LP))||(Milling,(FD/[C1]RD))),(HPHS/[C2]LPLS))",
    "impacts": {
      "FD": {
        "cost": 2.8
      },
      "HP": {
        "cost": 0.7
      },
      "Bending": {
        "cost": 0.001
      },
      "Milling": {
      },
      "HPHS": {
      },
      "RD": {
      },
      "Cutting": {
        "CO2": 10.0,
        "cost": 0.0
      },
      "LP": {
      },
      "LPLS": {
        "CO2": 10.0,
        "cost": 0.0
      }
    },
    "durations": {
      "FD": [
        0,
        1
      ],
      "HP": [
        0,
        1
      ],
      "Bending": [
        1,
        20
      ],
      "Milling": [
        0,
        1
      ],
      "HPHS": [
        0,
        1
      ],
      "RD": [
        0,
        1
      ],
      "Cutting": [
        0,
        1
      ],
      "LP": [
        0,
        1
      ],
      "LPLS": [
        0,
        1
      ]
    },
    "delays": {
      "C2": 2,
      "C1": 4
    },
    "probabilities": {
      "N1": 0.15
    },
    "loop_probability": {},
    "loop_round": {}
  }
}
    ''',

},

{
    "input": ''' I have a process where at the beginnig the user has to do 5 surveys (call them S1, S2,S3, ...) alltogheter. 
    Then, Based on the answer there is a nature that send me or in a T1 or T2. After I have 2 choises to make.
    ''',
    "answer": '''This is the updated BPMN dictionary with the process description.
    
    {
  "bpmn": {
    "expression": "(S1||S2||S3||S4||S5),(T1^[N1]T2),(C1/[C2]C2)",
    "impacts": {
      "T1": {
        "impacts": 0.0
      },
      "S3": {
        "impacts": 0.0
      },
      "S5": {
        "impacts": 0.0
      },
      "C1": {
        "impacts": 0.0
      },
      "T2": {
        "impacts": 0.0
      },
      "C2": {
        "impacts": 0.0
      },
      "S1": {
        "impacts": 0.0
      },
      "S2": {
        "impacts": 0.0
      },
      "S4": {
        "impacts": 0.0
      }
    },
    "durations": {
      "T1": [
        1,
        40
      ],
      "S3": [
        0,
        1
      ],
      "S5": [
        0,
        1
      ],
      "C1": [
        0,
        1
      ],
      "T2": [
        1,
        52
      ],
      "C2": [
        0,
        1
      ],
      "S1": [
        0,
        1
      ],
      "S2": [
        0,
        1
      ],
      "S4": [
        0,
        1
      ]
    },
    "delays": {
      "C2": 2
    },
    "probabilities": {
      "N1": 0.15
    },
    "loop_probability": {},
    "loop_round": {}
  }
}
    ''',

},


# {
#     "input": '''Now I have to complete the writing task before having a nature between talking with the publisher or to print the page written. Then, i choose between going to the park or continue writing''',
#     "answer": '''(Writing, (Talking with Publisher ^ [N1] Print Page), (Go to the Park / [C1] Continue Writing))''',

# },

{
    "input": '''
    Theprocess starts with a parallel split into two branches. The first branch contains a choice between task T1 and task T2. The second branch contains a nested nature split. This nested nature split has two branches:

    The first branch of the nested nature split contains another nature split between task T3 and task T4, followed by task TU1.
    The second branch of the nested nature split contains another nature split between task T5 and task T6, followed by task TU2.
    The nature splits are probabilistic, meaning that the decision to follow one branch or the other is based on a probability.

    In summary, the process involves a parallel split into two branches. The first branch contains a choice between T1 and T2. The second branch contains a nested nature split with two branches:

    The first branch of the nested nature split contains another nature split between T3 and T4, followed by TU1.
    The second branch of the nested nature split contains another nature split between T5 and T6, followed by TU2.
    ''',
    "answer": '''This is the updated BPMN dictionary with the process description.
    
    {
  "bpmn": {
    "expression": "((T1/[C1]T2)||(((T3^[N2]T4),TU1)^[N1]((T5^[N3]T6),TU2)))",
    "impacts": {
      "T1": {
        "impacts": 0.0
      },
      "T3": {
        "impacts": 0.0
      },
      "TU1": {
        "impacts": 0.0
      },
      "T2": {
        "impacts": 0.0
      },
      "TU2": {
        "impacts": 0.0
      },
      "T6": {
        "impacts": 0.0
      },
      "T4": {
        "impacts": 0.0
      },
      "T5": {
        "impacts": 0.0
      }
    },
    "durations": {
      "T1": [
        1,
        40
      ],
      "T3": [
        1,
        83
      ],
      "TU1": [
        0,
        1
      ],
      "T2": [
        1,
        52
      ],
      "TU2": [
        0,
        1
      ],
      "T6": [
        1,
        79
      ],
      "T4": [
        1,
        18
      ],
      "T5": [
        1,
        26
      ]
    },
    "delays": {
      "C1": 4
    },
    "probabilities": {
      "N2": 0.49,
      "N1": 0.15,
      "N3": 0.41
    },
    "loop_probability": {},
    "loop_round": {}
  }
}
    ''',

},

{
    "input": '''I have a process where I have to do a T0 and then I have to choose between T1 AND T2''',
    "answer": '''This is the updated BPMN dictionary with the process description.
    
    {
  "bpmn": {
    "expression": "T0,(T1/[C1]T2)",
    "impacts": {
      "T1": {
        "impacts": 0.0
      },
      "T2": {
        "impacts": 0.0
      },
      "T0": {
        "impacts": 0.0
      }
    },
    "durations": {
      "T1": [
        1,
        40
      ],
      "T2": [
        1,
        52
      ],
      "T0": [
        0,
        1
      ]
    },
    "delays": {
      "C1": 0
    },
    "probabilities": {},
    "loop_probability": {},
    "loop_round": {}
  }
}''',
},

{
    "input": '''A process where I have to do a SimpleTask1 and then I have a nature between Task1 and T2 ''',
    "answer": '''This is the updated BPMN dictionary with the process description.
    
    {
  "bpmn": {
    "expression": "SimpleTask1,(Task1^[N1]T2)",
    "impacts": {
      "SimpleTask1": {
        "impacts": 0.0
      },
      "T2": {
        "impacts": 0.0
      },
      "Task1": {
        "impacts": 0.0
      }
    },
    "durations": {
      "SimpleTask1": [
        0,
        1
      ],
      "T2": [
        1,
        52
      ],
      "Task1": [
        0,
        1
      ]
    },
    "delays": {},
    "probabilities": {
      "N1": 0.15
    },
    "loop_probability": {},
    "loop_round": {}
  }
}
    ''',

},



{
    "input": '''A process where I have to do a SimpleTask1 and then I have a nature between Task1 and T2 and then I have a nature between T3 and T4''',
    "answer": '''This is the updated BPMN dictionary with the process description.
    
    {
  "bpmn": {
    "expression": "SimpleTask1,(Task1^[N1]T2),(T3^[N2]T4)",
    "impacts": {
      "Task1": {
        "impacts": 0.0
      },
      "T4": {
        "impacts": 0.0
      },
      "T2": {
        "impacts": 0.0
      },
      "SimpleTask1": {
        "impacts": 0.0
      },
      "T3": {
        "impacts": 0.0
      }
    },
    "durations": {
      "Task1": [
        0,
        1
      ],
      "T4": [
        1,
        18
      ],
      "T2": [
        1,
        52
      ],
      "SimpleTask1": [
        0,
        1
      ],
      "T3": [
        1,
        83
      ]
    },
    "delays": {},
    "probabilities": {
      "N1": 0.15,
      "N2": 0.49
    },
    "loop_probability": {},
    "loop_round": {}
  }
}
    ''',

},



{
    "input": '''A process where I have a nature between TaskA and TaskB followed by Task2''',
    "answer": '''This is the updated BPMN dictionary with the process description.
    
    {
  "bpmn": {
    "expression": "(TaskA^[C1]TaskB,Task2)",
    "impacts": {
      "TaskB": {
        "impacts": 0.0
      },
      "Task2": {
        "impacts": 0.0
      },
      "TaskA": {
        "impacts": 0.0
      }
    },
    "durations": {
      "TaskB": [
        0,
        1
      ],
      "Task2": [
        0,
        1
      ],
      "TaskA": [
        0,
        1
      ]
    },
    "delays": {},
    "probabilities": {
      "C1": 0.5
    },
    "loop_probability": {},
    "loop_round": {}
  }
}''',

},


{
    "input": '''Fist I have a nature between HP and LP, then I have aNOTHER nature between HPHS and LPLS then a choice between t1 and t3, then t4 and t5''',
    "answer": '''This is the updated BPMN dictionary with the process description.
    {
  "bpmn": {
    "expression": "(HP^[N1]LP),(HPHS^[N2]LPLS),(t1/[c1]t3),t4,t5",
    "impacts": {
      "LP": {
        "impacts": 0.0
      },
      "t5": {
        "impacts": 0.0
      },
      "HP": {
        "impacts": 0.0
      },
      "t1": {
        "impacts": 0.0
      },
      "LPLS": {
        "impacts": 0.0
      },
      "t3": {
        "impacts": 0.0
      },
      "t4": {
        "impacts": 0.0
      },
      "HPHS": {
        "impacts": 0.0
      }
    },
    "durations": {
      "LP": [
        0,
        1
      ],
      "t5": [
        0,
        1
      ],
      "HP": [
        0,
        1
      ],
      "t1": [
        0,
        1
      ],
      "LPLS": [
        0,
        1
      ],
      "t3": [
        0,
        1
      ],
      "t4": [
        0,
        1
      ],
      "HPHS": [
        0,
        1
      ]
    },
    "delays": {
      "c1": 0
    },
    "probabilities": {
      "N1": 0.15,
      "N2": 0.49
    },
    "loop_probability": {},
    "loop_round": {}
  }
}
    ''',

},


# {
#     "input": '''''',
#     "answer": '''''',

# },

# {
#     "input": '''''',
#     "answer": '''''',

# },
]



a = {
'prompt' : '''

You are an assistant to design processes. In particular, 
your role is to pass from an user description of the process to the grammar defined using the python library lark and vice versa.  
Note that all process that you have to create are BPMN diagram that are single-entry-single-exit (SESE). 
Meaning that for all nodes you have only one element in exit and one incoming.        
There are few exceptions which are: natures or probabilistic split, choice and parallel. They have one entry but 2 exits.
That is because the the choices and the natures represents xor decisions while parallel represents 'and', so taking both the branches.
the grammar is """
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
""".
All the different section of the process are inserted in () and there can not be an empty region. These can be nested as (T1, (T2,T3)).
Here an example. 
User: 
depicts a metal manufacturing process that involves cutting, milling,
bending, polishing, depositioning, and painting a metal piece. 
First the cutting is done. Then, I have to do both:
- bending and then there is a nature that decides between heavy or light polishing
- milling, then I have a choice between fine or rough deposition
after this there is a choice between the hphs or lpls painting.
With this choice the process is concluded. 

The traduction is: (Cutting, ( (Bending, (HP ^ [N1]LP ) ) || ( Milling, ( FD / [C1] RD))), (HPHS / [C2] LPLS))

Another example: 
I have a process where at the beginnig the user has to do 5 surveys (call them S1, S2,S3, ...) alltogheter. 
Then, Based on the answer there is a nature that send me or in a T1 or T2. After I have 2 choises to make.

the traduction: (S1 || S2 || S3 || S4 || S5), (T1 ^ [N1] T2), (C1 / [C2] C2)

Another example:
I have a process where I do a simpletask1 before a task1
The traduction: (SimpleTask1, Task1)

Another example:
Now I have to complete the writing task before having a nature between talking with the publisher or to print the page written. Then, i choose between going to the park or continue writing
the traduction: (Writing, (Talking with Publisher ^ [N1] Print Page), (Go to the Park / [C1] Continue Writing))
''',

'prompt1' : '''
All the different section of the process are inserted in (). These can be nested as (T1, (T2,T3)). 
Moreover there can not be an empty region.
Now write your answer in sections. In particular, the first section has to have the summary with the translation of the process given and a second one where you provide the total answer. Now translate this process: i have a machine that melts a piece of iron. Then, the melted iron is divided into 2 different baskets. The first is cast into a nail shape and has to be individually checked. There is a probability that some are not correct; in this case, they are collected in a special bucket. if they are correct are packed and then shipped. The other iron is cast into cubes and are decided that are shipped to the customer or put into the warehouse. then if the shipped is made the accountant  send the bills.
''',
}