import unittest
import os

from src.paco.parser.bpmn_parser import create_parse_tree
from src.paco.saturate_execution.saturate_execution import saturate_execution_decisions
from src.paco.saturate_execution.states import States, states_info, ActivityState
from src.paco.parser.parse_tree import ParseTree
from src.paco.parser.parse_node import Sequential, Task, Nature, Choice, Parallel

from src.utils import check_syntax as cs
from src.utils.env import EXPRESSION, H, IMPACTS, DURATIONS, IMPACTS_NAMES, PROBABILITIES, DELAYS, LOOP_PROBABILITY, LOOP_ROUND


def test_create_parse_tree(bpmn: dict) -> ParseTree:
    bpmn[DURATIONS] = cs.set_max_duration(bpmn[DURATIONS])
    tmp = create_parse_tree(bpmn)
    return tmp[:-1]


class TestSaturateExecution(unittest.TestCase):
    def info(self, parse_tree, states, name):
        #parse_tree.print(outfile=self.directory + name)
        #parse_tree.to_json(outfile=self.directory + name)
        print(f"{name}:\n{states_info(states)}")

    def setUp(self):
        #pass
        self.directory = "output_files/saturate_execution/"
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    # Sequential Tests

    def test_sequential_tasks(self):
        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "T1, T2",
            H: 0,
            IMPACTS: {"T1": [11, 15], "T2": [4, 2]},
            DURATIONS: {"T1": [0, 1], "T2": [0, 2]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {}, DELAYS: {}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "sequential_tasks")


        s1 = Sequential(None, 0, 0)
        t1 = Task(s1, 0, 1, "T1", [], 1)
        t2 = Task(s1, 1, 2, "T2", [], 2)

        self.assertEqual(states.activityState[s1], ActivityState.COMPLETED_WITHOUT_PASSING_OVER,
                         "The root should be completed without passing over")
        self.assertEqual(states.executed_time[s1], 3,
                         "S1 should be executed with time 3")
        self.assertEqual(states.activityState[t1], ActivityState.COMPLETED,
                         "T1 should be completed")
        self.assertEqual(states.executed_time[t1], 1,
                         "T1 should be completed at time 1")
        self.assertEqual(states.activityState[t2], ActivityState.COMPLETED_WITHOUT_PASSING_OVER,
                         "T2 should be completed without passing over")
        self.assertEqual(states.executed_time[t2], 2,
                         "T2 should be completed at time 2")

    def test_sequential_nature_task(self):
        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "(T1 ^ [N1] T2), T3",
            H: 0,
            IMPACTS: {"T1": [11, 15], "T2": [4, 2], "T3": [1, 20]},
            DURATIONS: {"T1": [0, 1], "T2": [0, 2], "T3": [0, 2]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {"N1": 0.6}, DELAYS: {}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "sequential_nature_task")

        s1 = Sequential(None, 0, 0)
        n1 = Nature(s1, 0, 1,"N1", 0.6)
        t1 = Task(n1, 0, 2, "T1", [], 0)
        t2 = Task(n1, 1, 3, "T2", [], 0)
        t3 = Task(s1, 1, 4, "T3", [], 0)

        self.assertEqual(states.activityState[s1], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[s1], 0,
                         "S1 should be executed with time 0")
        self.assertEqual(states.activityState[n1], ActivityState.ACTIVE,
                         "N1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n1], 0,
                         "N1 never increases its executed time")
        self.assertEqual(states.activityState[t1], ActivityState.WAITING,
                         "T1 should be waiting, (waiting nature child A)")
        self.assertEqual(states.executed_time[t1], 0,
                         "T1 never increases its executed time")
        self.assertEqual(states.activityState[t2], ActivityState.WAITING,
                         "T2 should be waiting, (waiting nature child B)")
        self.assertEqual(states.executed_time[t2], 0,
                         "T2 never increases its executed time")
        self.assertEqual(states.activityState[t3], ActivityState.WAITING,
                         "T3 should be waiting")
        self.assertEqual(states.executed_time[t3], 0,
                         "T3 never increases its executed time")

        self.assertEqual(len(choices) + len(natures), 1, "There should be one nature")
        self.assertEqual(natures[0], n1, "The nature should be N1")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():

            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t1, "The first decision should be T1")
        self.assertEqual(multi_decisions[1][0], t2, "The second decision should be T2")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t1], ActivityState.ACTIVE, "T1 should be active")
        self.assertEqual(multi_branches[0].activityState[t2], ActivityState.WILL_NOT_BE_EXECUTED, "T2 will not be executed")

        self.assertEqual(multi_branches[1].activityState[t1], ActivityState.WILL_NOT_BE_EXECUTED, "T1 will not be executed")
        self.assertEqual(multi_branches[1].activityState[t2], ActivityState.ACTIVE, "T2 should be active")

    def test_sequential_task_nature(self):
        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "T1, (T2 ^ [N1] T3)",
            H: 0,
            IMPACTS: {"T1": [11, 15], "T2": [4, 2], "T3": [1, 20]},
            DURATIONS: {"T1": [0, 1], "T2": [0, 2], "T3": [0, 2]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {"N1": 0.6}, DELAYS: {}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "sequential_task_nature")

        s1 = Sequential(None, 0, 0)
        t1 = Task(s1, 0, 1, "T1", [], 0)
        n1 = Nature(s1, 1, 2,"N1", 0.6)
        t2 = Task(n1, 0, 3, "T2", [], 0)
        t3 = Task(s1, 1, 4, "T3", [], 0)

        self.assertEqual(states.activityState[s1], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[s1], 1,
                         "S1 should be executed with time 0")
        self.assertEqual(states.activityState[t1], ActivityState.COMPLETED_WITHOUT_PASSING_OVER,
                         "T1 should be completed without passing over")
        self.assertEqual(states.executed_time[t1], 1,
                         "T1 should be completed without passing over at time 1")
        self.assertEqual(states.activityState[n1], ActivityState.ACTIVE,
                         "N1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n1], 0,
                         "N1 never increases its executed time")
        self.assertEqual(states.activityState[t2], ActivityState.WAITING,
                         "T2 should be waiting, (waiting nature child A)")
        self.assertEqual(states.executed_time[t2], 0,
                         "T2 never increases its executed time")
        self.assertEqual(states.activityState[t3], ActivityState.WAITING,
                         "T3 should be waiting, (waiting nature child B)")
        self.assertEqual(states.executed_time[t3], 0,
                         "T3 never increases its executed time")

        self.assertEqual(len(choices) + len(natures), 1, "There should be one nature")
        self.assertEqual(natures[0], n1, "The nature should be N1")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t2, "The first decision should be T2")
        self.assertEqual(multi_decisions[1][0], t3, "The second decision should be T3")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t2], ActivityState.ACTIVE, "T2 should be active")
        self.assertEqual(multi_branches[0].activityState[t3], ActivityState.WILL_NOT_BE_EXECUTED, "T3 will not be executed")

        self.assertEqual(multi_branches[1].activityState[t2], ActivityState.WILL_NOT_BE_EXECUTED, "T2 will not be executed")
        self.assertEqual(multi_branches[1].activityState[t3], ActivityState.ACTIVE, "T3 should be active")

    def test_sequential_choice_task(self):
        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "(T1 / [C1] T2), T3",
            H: 0,
            IMPACTS: {"T1": [11, 15], "T2": [4, 2], "T3": [1, 20]},
            DURATIONS: {"T1": [0, 1], "T2": [0, 2], "T3": [0, 2]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {}, DELAYS: {"C1": 1}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "sequential_choice_task")

        s1 = Sequential(None, 0, 0)
        c1 = Nature(s1, 0, 1,"C1", 0.6)
        t1 = Task(c1, 0, 2, "T1", [], 0)
        t2 = Task(c1, 1, 3, "T2", [], 0)
        t3 = Task(s1, 1, 4, "T3", [], 0)

        self.assertEqual(states.activityState[s1], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[s1], 1,
                         "S1 should be executed with time 1")
        self.assertEqual(states.activityState[c1], ActivityState.ACTIVE,
                         "C1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c1], 1,
                         "C1 should be executed with time 1")
        self.assertEqual(states.activityState[t1], ActivityState.WAITING,
                         "T1 should be waiting, (waiting nature child A)")
        self.assertEqual(states.executed_time[t1], 0,
                         "T1 never increases its executed time")
        self.assertEqual(states.activityState[t2], ActivityState.WAITING,
                         "T2 should be waiting, (waiting nature child B)")
        self.assertEqual(states.executed_time[t2], 0,
                         "T2 never increases its executed time")
        self.assertEqual(states.activityState[t3], ActivityState.WAITING,
                         "T3 should be waiting")
        self.assertEqual(states.executed_time[t3], 0,
                         "T3 never increases its executed time")

        self.assertEqual(len(choices) +len(natures), 1, "There should be one choice")
        self.assertEqual(choices[0], c1, "The choice should be C1")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t1, "The first decision should be T1")
        self.assertEqual(multi_decisions[1][0], t2, "The second decision should be T2")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t1], ActivityState.ACTIVE, "T1 should be active")
        self.assertEqual(multi_branches[0].activityState[t2], ActivityState.WILL_NOT_BE_EXECUTED, "T2 will not be executed")

        self.assertEqual(multi_branches[1].activityState[t1], ActivityState.WILL_NOT_BE_EXECUTED, "T1 will not be executed")
        self.assertEqual(multi_branches[1].activityState[t2], ActivityState.ACTIVE, "T2 should be active")

    def test_sequential_task_choice(self):
        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "T1, (T2 / [C1] T3)",
            H: 0,
            IMPACTS: {"T1": [11, 15], "T2": [4, 2], "T3": [1, 20]},
            DURATIONS: {"T1": [0, 1], "T2": [0, 2], "T3": [0, 2]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {}, DELAYS: {"C1": 0}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)

        self.info(parse_tree, states, "sequential_task_choice")

        s1 = Sequential(None, 0, 0)
        t1 = Task(s1, 0, 1, "T1", [], 0)
        c1 = Choice(s1, 1, 2,"C1", 0)
        t2 = Task(c1, 0, 3, "T2", [], 0)
        t3 = Task(c1, 1, 4, "T3", [], 0)

        self.assertEqual(states.activityState[s1], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[s1], 1,
                         "S1 should be executed with time 0")
        self.assertEqual(states.activityState[t1], ActivityState.COMPLETED_WITHOUT_PASSING_OVER,
                         "T1 should be completed without passing over")
        self.assertEqual(states.executed_time[t1], 1,
                         "T1 should be completed without passing over at time 1")
        self.assertEqual(states.activityState[c1], ActivityState.ACTIVE,
                         "C1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c1], 0,
                         "C1 never increases its executed time")
        self.assertEqual(states.activityState[t2], ActivityState.WAITING,
                         "T2 should be waiting, (waiting nature child A)")
        self.assertEqual(states.executed_time[t2], 0,
                         "T2 never increases its executed time")
        self.assertEqual(states.activityState[t3], ActivityState.WAITING,
                         "T3 should be waiting, (waiting nature child B)")
        self.assertEqual(states.executed_time[t3], 0,
                         "T3 never increases its executed time")

        self.assertEqual(len(choices) + len(natures), 1, "There should be one choice")
        self.assertEqual(choices[0], c1, "The choice should be C1")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t2, "The first decision should be T2")
        self.assertEqual(multi_decisions[1][0], t3, "The second decision should be T3")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t2], ActivityState.ACTIVE, "T2 should be active")
        self.assertEqual(multi_branches[0].activityState[t3], ActivityState.WILL_NOT_BE_EXECUTED, "T3 will not be executed")

        self.assertEqual(multi_branches[1].activityState[t2], ActivityState.WILL_NOT_BE_EXECUTED, "T2 will not be executed")
        self.assertEqual(multi_branches[1].activityState[t3], ActivityState.ACTIVE, "T3 should be active")

    # Sequential Sequential Tests

    def test_sequential_sequential_nature(self):
        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "T1, T2,(T3 ^ [N1] T4)",
            H: 0,
            IMPACTS: {"T1": [1, 2], "T2": [3, 4], "T3": [5, 6], "T4": [7, 8]},
            DURATIONS: {"T1": [0, 0], "T2": [0, 1], "T3": [0, 2], "T4": [0, 3]},
            IMPACTS_NAMES: ["a", "b"],
            PROBABILITIES: {"N1": 0.6}, DELAYS: {}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "sequential_sequential_nature")

        s1 = Sequential(None, 0, 0)
        t1 = Task(s1, 0, 2, "T1", [], 0)
        t2 = Task(s1, 1, 3, "T2", [], 0)
        n1 = Nature(s1, 1, 4, "N1", 0.6)
        t3 = Task(n1, 0, 5, "T3", [], 0)
        t4 = Task(n1, 1, 6, "T4", [], 0)

        self.assertEqual(states.activityState[s1], ActivityState.ACTIVE, "The root should be active")
        self.assertEqual(states.executed_time[s1], 1, "S1 should be executed with time 1")

        self.assertEqual(states.activityState[t1], ActivityState.COMPLETED, "T1 should be completed")
        self.assertEqual(states.executed_time[t1], 0, "T1 should be completed at time 0")
        self.assertEqual(states.activityState[t2], ActivityState.COMPLETED_WITHOUT_PASSING_OVER, "T2 should be completed without passing over")
        self.assertEqual(states.executed_time[t2], 1, "T2 should be completed at time 1")

        self.assertEqual(states.activityState[n1], ActivityState.ACTIVE, "N1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n1], 0, "N1 never increases its executed time")
        self.assertEqual(states.activityState[t3], ActivityState.WAITING, "T3 should be waiting")
        self.assertEqual(states.activityState[t4], ActivityState.WAITING, "T4 should be waiting")
        self.assertEqual(states.executed_time[t3], 0, "T3 never increases its executed time")
        self.assertEqual(states.executed_time[t4], 0, "T4 never increases its executed time")

        self.assertEqual(len(choices) + len(natures), 1, "There should be one nature")
        self.assertEqual(natures[0], n1, "The nature should be N1")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t3, "The first decision should be T3")
        self.assertEqual(multi_decisions[1][0], t4, "The second decision should be T4")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t3], ActivityState.ACTIVE, "T3 should be active")
        self.assertEqual(multi_branches[0].activityState[t4], ActivityState.WILL_NOT_BE_EXECUTED, "T4 should be waiting")

        self.assertEqual(multi_branches[1].activityState[t3], ActivityState.WILL_NOT_BE_EXECUTED, "T3 should be waiting")
        self.assertEqual(multi_branches[1].activityState[t4], ActivityState.ACTIVE, "T4 should be active")

    def test_sequential_sequential_choice(self):
        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "T1, T2,(T3 / [C1] T4)",
            H: 0,
            IMPACTS: {"T1": [1, 2], "T2": [3, 4], "T3": [5, 6], "T4": [7, 8]},
            DURATIONS: {"T1": [0, 0], "T2": [0, 1], "T3": [0, 2], "T4": [0, 3]},
            IMPACTS_NAMES: ["a", "b"],
            PROBABILITIES: {}, DELAYS: {"C1": 0}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "sequential_sequential_choice")

        s1 = Sequential(None, 0, 0)
        t1 = Task(s1, 0, 2, "T1", [], 0)
        t2 = Task(s1, 1, 3, "T2", [], 0)
        c1 = Nature(s1, 1, 4, "N1", 0.6)
        t3 = Task(c1, 0, 5, "T3", [], 0)
        t4 = Task(c1, 1, 6, "T4", [], 0)

        self.assertEqual(states.activityState[s1], ActivityState.ACTIVE, "The root should be active")
        self.assertEqual(states.executed_time[s1], 1, "S1 should be executed with time 1")

        self.assertEqual(states.activityState[t1], ActivityState.COMPLETED, "T1 should be completed")
        self.assertEqual(states.executed_time[t1], 0, "T1 should be completed at time 0")
        self.assertEqual(states.activityState[t2], ActivityState.COMPLETED_WITHOUT_PASSING_OVER, "T2 should be completed without passing over")
        self.assertEqual(states.executed_time[t2], 1, "T2 should be completed at time 1")
        self.assertEqual(states.activityState[c1], ActivityState.ACTIVE, "C1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c1], 0, "C1 not increases its executed time")
        self.assertEqual(states.activityState[t3], ActivityState.WAITING, "T3 should be waiting")
        self.assertEqual(states.activityState[t4], ActivityState.WAITING, "T4 should be waiting")
        self.assertEqual(states.executed_time[t3], 0, "T3 never increases its executed time")
        self.assertEqual(states.executed_time[t4], 0, "T4 never increases its executed time")

        self.assertEqual(len(choices) + len(natures), 1, "There should be one choice")
        self.assertEqual(choices[0], c1, "The choice should be C1")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t3, "The first decision should be T3")
        self.assertEqual(multi_decisions[1][0], t4, "The second decision should be T4")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t3], ActivityState.ACTIVE, "T3 should be active")
        self.assertEqual(multi_branches[0].activityState[t4], ActivityState.WILL_NOT_BE_EXECUTED, "T4 should be waiting")

        self.assertEqual(multi_branches[1].activityState[t3], ActivityState.WILL_NOT_BE_EXECUTED, "T3 should be waiting")
        self.assertEqual(multi_branches[1].activityState[t4], ActivityState.ACTIVE, "T4 should be active")

        # Considering choice delay
        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "T1, T2,(T3 / [C1] T4)",
            H: 0,
            IMPACTS: {"T1": [1, 2], "T2": [3, 4], "T3": [5, 6], "T4": [7, 8]},
            DURATIONS: {"T1": [0, 0], "T2": [0, 1], "T3": [0, 2], "T4": [0, 3]},
            IMPACTS_NAMES: ["a", "b"],
            PROBABILITIES: {}, DELAYS: {"C1": 1}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "sequential_sequential_choice_delay")

        self.assertEqual(states.activityState[s1], ActivityState.ACTIVE, "The root should be active")
        self.assertEqual(states.executed_time[s1], 2, "S1 should be executed with time 2")

        self.assertEqual(states.activityState[t1], ActivityState.COMPLETED, "T1 should be completed")
        self.assertEqual(states.executed_time[t1], 0, "T1 should be completed at time 0")

        self.assertEqual(states.activityState[t2], ActivityState.COMPLETED, "T2 should be completed because of the choice delay")
        self.assertEqual(states.executed_time[t2], 1, "T2 should be completed at time 1")

        self.assertEqual(states.activityState[c1], ActivityState.ACTIVE, "C1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c1], 1, "C1 increases its executed time to 1")
        self.assertEqual(states.activityState[t3], ActivityState.WAITING, "T3 should be waiting")
        self.assertEqual(states.activityState[t4], ActivityState.WAITING, "T4 should be waiting")
        self.assertEqual(states.executed_time[t3], 0, "T3 never increases its executed time")
        self.assertEqual(states.executed_time[t4], 0, "T4 never increases its executed time")

        self.assertEqual(len(choices) + len(natures), 1, "There should be one choice")
        self.assertEqual(choices[0], c1, "The choice should be C1")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t3, "The first decision should be T3")
        self.assertEqual(multi_decisions[1][0], t4, "The second decision should be T4")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t3], ActivityState.ACTIVE, "T3 should be active")
        self.assertEqual(multi_branches[0].activityState[t4], ActivityState.WILL_NOT_BE_EXECUTED, "T4 should be waiting")

        self.assertEqual(multi_branches[1].activityState[t3], ActivityState.WILL_NOT_BE_EXECUTED, "T3 should be waiting")
        self.assertEqual(multi_branches[1].activityState[t4], ActivityState.ACTIVE, "T4 should be active")

    # Parallel Tests

    def test_parallel_tasks(self):
        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "T1 || T2",
            H: 0,
            IMPACTS: {"T1": [11, 15], "T2": [4, 2]},
            DURATIONS: {"T1": [0, 1], "T2": [0, 1]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {}, DELAYS: {}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "parallel_task1_eq_task2")

        p1 = Parallel(None, 0, 0)
        t1 = Task(p1, 0, 1, "T1", [], 1)
        t2 = Task(p1, 1, 2, "T2", [], 2)


        self.assertEqual(states.activityState[p1], ActivityState.COMPLETED_WITHOUT_PASSING_OVER,
                         "The root should be completed without passing over")
        self.assertEqual(states.executed_time[p1], 1,
                         "P1 should be executed with time 1")
        self.assertEqual(states.activityState[t1], ActivityState.COMPLETED_WITHOUT_PASSING_OVER,
                         "T1 should be completed without passing over")
        self.assertEqual(states.executed_time[t1], 1,
                         "T1 should be completed at time 1")
        self.assertEqual(states.activityState[t2], ActivityState.COMPLETED_WITHOUT_PASSING_OVER,
                         "T2 should be completed without passing over")
        self.assertEqual(states.executed_time[t2], 1,
                         "T2 should be completed at time 1")


        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "T1 || T2",
            H: 0,
            IMPACTS: {"T1": [11, 15], "T2": [4, 2]},
            DURATIONS: {"T1": [0, 1], "T2": [0, 2]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {}, DELAYS: {}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "parallel_task1_lt_task2")


        self.assertEqual(states.activityState[p1], ActivityState.COMPLETED_WITHOUT_PASSING_OVER,
                         "The root should be completed without passing over")
        self.assertEqual(states.executed_time[p1], 2,
                         "P1 should be executed with time 2")
        self.assertEqual(states.activityState[t1], ActivityState.COMPLETED,
                         "T1 should be completed")
        self.assertEqual(states.executed_time[t1], 1,
                         "T1 should be completed at time 1")
        self.assertEqual(states.activityState[t2], ActivityState.COMPLETED_WITHOUT_PASSING_OVER,
                         "T2 should be completed without passing over")
        self.assertEqual(states.executed_time[t2], 2,
                         "T2 should be completed at time 2")

        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "T1 || T2",
            H: 0,
            IMPACTS: {"T1": [11, 15], "T2": [4, 2]},
            DURATIONS: {"T1": [0, 2], "T2": [0, 1]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {}, DELAYS: {}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "parallel_task1_gt_task2")

        self.assertEqual(states.activityState[p1], ActivityState.COMPLETED_WITHOUT_PASSING_OVER,
                         "The root should be completed without passing over")
        self.assertEqual(states.executed_time[p1], 2,
                         "P1 should be executed with time 2")
        self.assertEqual(states.activityState[t1], ActivityState.COMPLETED_WITHOUT_PASSING_OVER,
                         "T1 should be completed without passing over")
        self.assertEqual(states.executed_time[t1], 2,
                         "T1 should be completed at time 2")
        self.assertEqual(states.activityState[t2], ActivityState.COMPLETED,
                         "T2 should be completed")
        self.assertEqual(states.executed_time[t2], 1,
                         "T2 should be completed at time 1")

    def test_parallel_choice_task(self):
        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "(T2 / [C1] T3) || T1",
            H: 0,
            IMPACTS: {"T1": [11, 15], "T2": [4, 2], "T3": [1, 20]},
            DURATIONS: {"T1": [0, 1], "T2": [0, 10], "T3": [1, 20]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {}, DELAYS: {"C1": 1}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "parallel_choice_eq_task")

        p1 = Parallel(None, 0, 0)
        c1 = Choice(p1, 0, 1, "C1", 1)
        t1 = Task(p1, 1, 4, "T1", [], 1)
        t2 = Task(p1, 0, 2, "T2", [], 2)
        t3 = Task(c1, 1, 3, "T3", [], 1)

        self.assertEqual(states.activityState[p1], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[p1], 1,
                         "P1 should be executed with time 1")
        self.assertEqual(states.activityState[c1], ActivityState.ACTIVE,
                         "C1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c1], 1,
                         "C1 should be executed with time 1")
        self.assertEqual(states.activityState[t2], ActivityState.WAITING,
                         "T2 should be waiting")
        self.assertEqual(states.executed_time[t2], 0,
                         "T2 never increases its executed time")
        self.assertEqual(states.activityState[t3], ActivityState.WAITING,
                         "T3 should be waiting")
        self.assertEqual(states.executed_time[t3], 0,
                         "T3 never increases its executed time")
        self.assertEqual(states.activityState[t1], ActivityState.COMPLETED_WITHOUT_PASSING_OVER,
                         "T1 should be completed without passing over")
        self.assertEqual(states.executed_time[t1], 1,
                         "T1 should be completed at time 1")

        self.assertEqual(len(choices) + len(natures), 1, "There should be one choice")
        self.assertEqual(choices[0], c1, "The choice should be C1")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t2, "The first decision should be T2")
        self.assertEqual(multi_decisions[1][0], t3, "The second decision should be T3")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")

        self.assertEqual(multi_branches[0].activityState[t2], ActivityState.ACTIVE, "T2 should be active")
        self.assertEqual(multi_branches[0].activityState[t3], ActivityState.WILL_NOT_BE_EXECUTED, "T3 should be waiting")

        self.assertEqual(multi_branches[1].activityState[t2], ActivityState.WILL_NOT_BE_EXECUTED, "T2 should be waiting")
        self.assertEqual(multi_branches[1].activityState[t3], ActivityState.ACTIVE, "T3 should be active")


        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "(T2 / [C1] T3) || T1",
            H: 0,
            IMPACTS: {"T1": [11, 15], "T2": [4, 2], "T3": [1, 20]},
            DURATIONS: {"T1": [0, 2], "T2": [0, 10], "T3": [1, 20]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {}, DELAYS: {"C1": 1}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "parallel_choice_lt_task")

        self.assertEqual(states.activityState[p1], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[p1], 1,
                         "P1 should be executed with time 1")
        self.assertEqual(states.activityState[c1], ActivityState.ACTIVE,
                         "C1 should be completed without passing over")
        self.assertEqual(states.executed_time[c1], 1,
                         "C1 should be completed at time 1")
        self.assertEqual(states.activityState[t2], ActivityState.WAITING,
                         "T2 should be waiting")
        self.assertEqual(states.executed_time[t2], 0,
                         "T2 never increases its executed time")
        self.assertEqual(states.activityState[t3], ActivityState.WAITING,
                         "T3 should be waiting")
        self.assertEqual(states.executed_time[t3], 0,
                         "T3 never increases its executed time")
        self.assertEqual(states.activityState[t1], ActivityState.ACTIVE,
                         "T1 should be active")
        self.assertEqual(states.executed_time[t1], 1,
                         "T1 should be completed at time 1")

        self.assertEqual(len(choices) + len(natures), 1, "There should be one choice")
        self.assertEqual(choices[0], c1, "The choice should be C1")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t2, "The first decision should be T2")
        self.assertEqual(multi_decisions[1][0], t3, "The second decision should be T3")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")

        self.assertEqual(multi_branches[0].activityState[t2], ActivityState.ACTIVE, "T2 should be active")
        self.assertEqual(multi_branches[0].activityState[t3], ActivityState.WILL_NOT_BE_EXECUTED, "T3 should be waiting")

        self.assertEqual(multi_branches[1].activityState[t2], ActivityState.WILL_NOT_BE_EXECUTED, "T2 should be waiting")
        self.assertEqual(multi_branches[1].activityState[t3], ActivityState.ACTIVE, "T3 should be active")


        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "(T2 / [C1] T3) || T1",
            H: 0,
            IMPACTS: {"T1": [11, 15], "T2": [4, 2], "T3": [1, 20]},
            DURATIONS: {"T1": [0, 1], "T2": [0, 10], "T3": [1, 20]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {}, DELAYS: {"C1": 2}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "parallel_choice_gt_task")

        self.assertEqual(states.activityState[p1], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[p1], 2,
                         "P1 should be executed with time 2")
        self.assertEqual(states.activityState[c1], ActivityState.ACTIVE,
                         "C1 should be completed without passing over")
        self.assertEqual(states.executed_time[c1], 2,
                         "C1 should be completed at time 2")
        self.assertEqual(states.activityState[t2], ActivityState.WAITING,
                         "T2 should be waiting")
        self.assertEqual(states.executed_time[t2], 0,
                         "T2 never increases its executed time")
        self.assertEqual(states.activityState[t3], ActivityState.WAITING,
                         "T3 should be waiting")
        self.assertEqual(states.executed_time[t3], 0,
                         "T3 never increases its executed time")
        self.assertEqual(states.activityState[t1], ActivityState.COMPLETED,
                         "T1 should be completed")
        self.assertEqual(states.executed_time[t1], 1,
                         "T1 should be completed at time 1")

        self.assertEqual(len(choices) +len(natures), 1, "There should be one choice")
        self.assertEqual(choices[0], c1, "The choice should be C1")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t2, "The first decision should be T2")
        self.assertEqual(multi_decisions[1][0], t3, "The second decision should be T3")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")

        self.assertEqual(multi_branches[0].activityState[t2], ActivityState.ACTIVE, "T2 should be active")
        self.assertEqual(multi_branches[0].activityState[t3], ActivityState.WILL_NOT_BE_EXECUTED, "T3 should be waiting")

        self.assertEqual(multi_branches[1].activityState[t2], ActivityState.WILL_NOT_BE_EXECUTED, "T2 should be waiting")
        self.assertEqual(multi_branches[1].activityState[t3], ActivityState.ACTIVE, "T3 should be active")

    # TODO use parallel_natures, parallel_choices, parallel_nature_choice for the solver test

    def test_parallel_natures(self):
        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "(T1A ^[N1] T1B) || (T2A ^[N2] T2B)",
            H: 0,
            IMPACTS: {"T1A": [0, 1], "T1B": [0, 2], "T2A": [0, 3], "T2B": [0, 4]},
            DURATIONS: {"T1A": [0, 1], "T1B": [0, 2], "T2A": [0, 3], "T2B": [0, 4]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {"N1": 0.6, "N2": 0.7}, DELAYS: {}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "parallel_natures")

        p1 = Parallel(None, 0, 0)
        n1 = Nature(p1, 0, 1, "N1", 0.6)
        t1a = Task(p1, 0, 2, "T1A", [], 0)
        t1b = Task(p1, 1, 3, "T1B", [], 0)

        n2 = Nature(p1, 1, 4, "N2", 0.7)
        t2a = Task(p1, 0, 5, "T2A", [], 0)
        t2b = Task(p1, 1, 6, "T2B", [], 0)

        self.assertEqual(states.activityState[p1], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[p1], 0,
                         "P1 should be executed with time 0")
        self.assertEqual(states.activityState[n1], ActivityState.ACTIVE,
                         "N1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n1], 0,
                         "N1 should be executed with time 0")
        self.assertEqual(states.activityState[t1a], ActivityState.WAITING,
                         "T1A should be waiting")
        self.assertEqual(states.executed_time[t1a], 0,
                         "T1A never increases its executed time")
        self.assertEqual(states.activityState[t1b], ActivityState.WAITING,
                         "T1B should be waiting")
        self.assertEqual(states.executed_time[t1b], 0,
                         "T1B never increases its executed time")
        self.assertEqual(states.activityState[n2], ActivityState.ACTIVE,
                         "N2 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n2], 0,
                         "N2 should be executed with time 0")
        self.assertEqual(states.activityState[t2a], ActivityState.WAITING,
                         "T2A should be waiting")
        self.assertEqual(states.executed_time[t2a], 0,
                         "T2A never increases its executed time")
        self.assertEqual(states.activityState[t2b], ActivityState.WAITING,
                         "T2B should be waiting")
        self.assertEqual(states.executed_time[t2b], 0,
                         "T2B never increases its executed time")

        self.assertEqual(len(choices) + len(natures), 2, "There should be two natures")
        self.assertEqual(natures[0], n1, "One nature should be N1")
        self.assertEqual(natures[1], n2, "One nature should be N2")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 4, "There should be 4 decisions")
        self.assertEqual(multi_decisions[0][0], t1a, "The first decision should be (T1A, T2A)")
        self.assertEqual(multi_decisions[0][1], t2a, "The first decision should be (T1A, T2A)")

        self.assertEqual(multi_decisions[1][0], t1a, "The second decision should be (T1A, T2B)")
        self.assertEqual(multi_decisions[1][1], t2b, "The second decision should be (T1A, T2B)")

        self.assertEqual(multi_decisions[2][0], t1b, "The third decision should be (T1B, T2A)")
        self.assertEqual(multi_decisions[2][1], t2a, "The third decision should be (T1B, T2A)")

        self.assertEqual(multi_decisions[3][0], t1b, "The fourth decision should be (T1B, T2B)")
        self.assertEqual(multi_decisions[3][1], t2b, "The fourth decision should be (T1B, T2B)")


        self.assertEqual(len(multi_branches), 4, "There should be 4 branches")

        self.assertEqual(multi_branches[0].activityState[t1a], ActivityState.ACTIVE, "T1A should be active")
        self.assertEqual(multi_branches[0].activityState[t1b], ActivityState.WILL_NOT_BE_EXECUTED, "T1B should be will not be executed")
        self.assertEqual(multi_branches[0].activityState[t2a], ActivityState.ACTIVE, "T2A should be active")
        self.assertEqual(multi_branches[0].activityState[t2b], ActivityState.WILL_NOT_BE_EXECUTED, "T2B should be will not be executed")

        self.assertEqual(multi_branches[1].activityState[t1a], ActivityState.ACTIVE, "T1A should be active")
        self.assertEqual(multi_branches[1].activityState[t1b], ActivityState.WILL_NOT_BE_EXECUTED, "T1B should be will not be executed")
        self.assertEqual(multi_branches[1].activityState[t2a], ActivityState.WILL_NOT_BE_EXECUTED, "T2A should be will not be executed")
        self.assertEqual(multi_branches[1].activityState[t2b], ActivityState.ACTIVE, "T2B should be active")

        self.assertEqual(multi_branches[2].activityState[t1a], ActivityState.WILL_NOT_BE_EXECUTED, "T1A should be active")
        self.assertEqual(multi_branches[2].activityState[t1b], ActivityState.ACTIVE, "T1B should be will not be executed")
        self.assertEqual(multi_branches[2].activityState[t2a], ActivityState.ACTIVE, "T2A should be active")
        self.assertEqual(multi_branches[2].activityState[t2b], ActivityState.WILL_NOT_BE_EXECUTED, "T2B should be will not be executed")

        self.assertEqual(multi_branches[3].activityState[t1a], ActivityState.WILL_NOT_BE_EXECUTED, "T1A should be active")
        self.assertEqual(multi_branches[3].activityState[t1b], ActivityState.ACTIVE, "T1B should be will not be executed")
        self.assertEqual(multi_branches[3].activityState[t2a], ActivityState.WILL_NOT_BE_EXECUTED, "T2A should be will not be executed")
        self.assertEqual(multi_branches[3].activityState[t2b], ActivityState.ACTIVE, "T2B should be active")

    def test_parallel_choices(self):
        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "(T1A /[C1] T1B) || (T2A /[C2] T2B)",
            H: 0,
            IMPACTS: {"T1A": [0, 1], "T1B": [0, 2], "T2A": [0, 3], "T2B": [0, 4]},
            DURATIONS: {"T1A": [0, 1], "T1B": [0, 2], "T2A": [0, 3], "T2B": [0, 4]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {}, DELAYS: {"C1": 1, "C2": 1}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "parallel_choice_eq_choice")

        p1 = Parallel(None, 0, 0)
        c1 = Choice(p1, 0, 1, "C1", 1)
        t1a = Task(p1, 0, 2, "T1A", [], 0)
        t1b = Task(p1, 1, 3, "T1B", [], 0)

        c2 = Choice(p1, 1, 4, "C2", 1)
        t2a = Task(p1, 0, 5, "T2A", [], 0)
        t2b = Task(p1, 1, 6, "T2B", [], 0)

        self.assertEqual(states.activityState[p1], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[p1], 1,
                         "P1 should be executed with time 1")
        self.assertEqual(states.activityState[c1], ActivityState.ACTIVE,
                         "C1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c1], 1,
                         "C1 should be executed with time 1")
        self.assertEqual(states.activityState[t1a], ActivityState.WAITING,
                         "T1A should be waiting")
        self.assertEqual(states.executed_time[t1a], 0,
                         "T1A never increases its executed time")
        self.assertEqual(states.activityState[t1b], ActivityState.WAITING,
                         "T1B should be waiting")
        self.assertEqual(states.executed_time[t1b], 0,
                         "T1B never increases its executed time")
        self.assertEqual(states.activityState[c2], ActivityState.ACTIVE,
                         "C2 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c2], 1,
                         "C2 should be executed with time 1")
        self.assertEqual(states.activityState[t2a], ActivityState.WAITING,
                         "T2A should be waiting")
        self.assertEqual(states.executed_time[t2a], 0,
                         "T2A never increases its executed time")
        self.assertEqual(states.activityState[t2b], ActivityState.WAITING,
                         "T2B should be waiting")
        self.assertEqual(states.executed_time[t2b], 0,
                         "T2B never increases its executed time")

        self.assertEqual(len(choices) + len(natures), 2, "There should be two choices")
        self.assertEqual(choices[0], c1, "One choice should be C1")
        self.assertEqual(choices[1], c2, "One choice should be C2")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 4, "There should be 4 decisions")
        self.assertEqual(multi_decisions[0][0], t1a, "The first decision should be (T1A, T2A)")
        self.assertEqual(multi_decisions[0][1], t2a, "The first decision should be (T1A, T2A)")

        self.assertEqual(multi_decisions[1][0], t1a, "The second decision should be (T1A, T2B)")
        self.assertEqual(multi_decisions[1][1], t2b, "The second decision should be (T1A, T2B)")

        self.assertEqual(multi_decisions[2][0], t1b, "The third decision should be (T1B, T2A)")
        self.assertEqual(multi_decisions[2][1], t2a, "The third decision should be (T1B, T2A)")

        self.assertEqual(multi_decisions[3][0], t1b, "The fourth decision should be (T1B, T2B)")
        self.assertEqual(multi_decisions[3][1], t2b, "The fourth decision should be (T1B, T2B)")


        self.assertEqual(len(multi_branches), 4, "There should be 4 branches")

        self.assertEqual(multi_branches[0].activityState[t1a], ActivityState.ACTIVE, "T1A should be active")
        self.assertEqual(multi_branches[0].activityState[t1b], ActivityState.WILL_NOT_BE_EXECUTED, "T1B should be will not be executed")
        self.assertEqual(multi_branches[0].activityState[t2a], ActivityState.ACTIVE, "T2A should be active")
        self.assertEqual(multi_branches[0].activityState[t2b], ActivityState.WILL_NOT_BE_EXECUTED, "T2B should be will not be executed")

        self.assertEqual(multi_branches[1].activityState[t1a], ActivityState.ACTIVE, "T1A should be active")
        self.assertEqual(multi_branches[1].activityState[t1b], ActivityState.WILL_NOT_BE_EXECUTED, "T1B should be will not be executed")
        self.assertEqual(multi_branches[1].activityState[t2a], ActivityState.WILL_NOT_BE_EXECUTED, "T2A should be will not be executed")
        self.assertEqual(multi_branches[1].activityState[t2b], ActivityState.ACTIVE, "T2B should be active")

        self.assertEqual(multi_branches[2].activityState[t1a], ActivityState.WILL_NOT_BE_EXECUTED, "T1A should be active")
        self.assertEqual(multi_branches[2].activityState[t1b], ActivityState.ACTIVE, "T1B should be will not be executed")
        self.assertEqual(multi_branches[2].activityState[t2a], ActivityState.ACTIVE, "T2A should be active")
        self.assertEqual(multi_branches[2].activityState[t2b], ActivityState.WILL_NOT_BE_EXECUTED, "T2B should be will not be executed")

        self.assertEqual(multi_branches[3].activityState[t1a], ActivityState.WILL_NOT_BE_EXECUTED, "T1A should be active")
        self.assertEqual(multi_branches[3].activityState[t1b], ActivityState.ACTIVE, "T1B should be will not be executed")
        self.assertEqual(multi_branches[3].activityState[t2a], ActivityState.WILL_NOT_BE_EXECUTED, "T2A should be will not be executed")
        self.assertEqual(multi_branches[3].activityState[t2b], ActivityState.ACTIVE, "T2B should be active")


        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "(T1A /[C1] T1B) || (T2A /[C2] T2B)",
            H: 0,
            IMPACTS: {"T1A": [0, 1], "T1B": [0, 2], "T2A": [0, 3], "T2B": [0, 4]},
            DURATIONS: {"T1A": [0, 1], "T1B": [0, 2], "T2A": [0, 3], "T2B": [0, 4]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {}, DELAYS: {"C1": 1, "C2": 2}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "parallel_choice_lt_choice")

        self.assertEqual(states.activityState[p1], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[p1], 1,
                         "P1 should be executed with time 1")
        self.assertEqual(states.activityState[c1], ActivityState.ACTIVE,
                         "C1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c1], 1,
                         "C1 should be executed with time 1")
        self.assertEqual(states.activityState[t1a], ActivityState.WAITING,
                         "T1A should be waiting")
        self.assertEqual(states.executed_time[t1a], 0,
                         "T1A never increases its executed time")
        self.assertEqual(states.activityState[t1b], ActivityState.WAITING,
                         "T1B should be waiting")
        self.assertEqual(states.executed_time[t1b], 0,
                         "T1B never increases its executed time")
        self.assertEqual(states.activityState[c2], ActivityState.ACTIVE,
                         "C2 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c2], 1,
                         "C2 should be executed with time 0")
        self.assertEqual(states.activityState[t2a], ActivityState.WAITING,
                         "T2A should be waiting")
        self.assertEqual(states.executed_time[t2a], 0,
                         "T2A never increases its executed time")
        self.assertEqual(states.activityState[t2b], ActivityState.WAITING,
                         "T2B should be waiting")
        self.assertEqual(states.executed_time[t2b], 0,
                         "T2B never increases its executed time")

        self.assertEqual(len(choices) +len(natures), 1, "There should be one choice")
        self.assertEqual(choices[0], c1, "The choice should be C1")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t1a, "The first decision should be T1A")
        self.assertEqual(multi_decisions[1][0], t1b, "The second decision should be T1B")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t1a], ActivityState.ACTIVE, "T1A should be active")
        self.assertEqual(multi_branches[0].activityState[t1b], ActivityState.WILL_NOT_BE_EXECUTED, "T1B should be waiting")

        self.assertEqual(multi_branches[1].activityState[t1a], ActivityState.WILL_NOT_BE_EXECUTED, "T1A should be waiting")
        self.assertEqual(multi_branches[1].activityState[t1b], ActivityState.ACTIVE, "T1B should be active")


        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "(T1A /[C1] T1B) || (T2A /[C2] T2B)",
            H: 0,
            IMPACTS: {"T1A": [0, 1], "T1B": [0, 2], "T2A": [0, 3], "T2B": [0, 4]},
            DURATIONS: {"T1A": [0, 1], "T1B": [0, 2], "T2A": [0, 3], "T2B": [0, 4]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {}, DELAYS: {"C1": 2, "C2": 1}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "parallel_choice_gt_choice")

        self.assertEqual(states.activityState[p1], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[p1], 1,
                         "P1 should be executed with time 1")
        self.assertEqual(states.activityState[c1], ActivityState.ACTIVE,
                         "C1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c1], 1,
                         "C1 should be executed with time 1")
        self.assertEqual(states.activityState[t1a], ActivityState.WAITING,
                         "T1A should be waiting")
        self.assertEqual(states.executed_time[t1a], 0,
                         "T1A never increases its executed time")
        self.assertEqual(states.activityState[t1b], ActivityState.WAITING,
                         "T1B should be waiting")
        self.assertEqual(states.executed_time[t1b], 0,
                         "T1B never increases its executed time")
        self.assertEqual(states.activityState[c2], ActivityState.ACTIVE,
                         "C2 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c2], 1,
                         "C2 should be executed with time 0")
        self.assertEqual(states.activityState[t2a], ActivityState.WAITING,
                         "T2A should be waiting")
        self.assertEqual(states.executed_time[t2a], 0,
                         "T2A never increases its executed time")
        self.assertEqual(states.activityState[t2b], ActivityState.WAITING,
                         "T2B should be waiting")
        self.assertEqual(states.executed_time[t2b], 0,
                         "T2B never increases its executed time")

        self.assertEqual(len(choices) + len(natures), 1, "There should be one choice")
        self.assertEqual(choices[0], c2, "The choice should be C2")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t2a, "The first decision should be T2A")
        self.assertEqual(multi_decisions[1][0], t2b, "The second decision should be T2B")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t2a], ActivityState.ACTIVE, "T1A should be active")
        self.assertEqual(multi_branches[0].activityState[t2b], ActivityState.WILL_NOT_BE_EXECUTED, "T1B should be waiting")

        self.assertEqual(multi_branches[1].activityState[t2a], ActivityState.WILL_NOT_BE_EXECUTED, "T1A should be waiting")
        self.assertEqual(multi_branches[1].activityState[t2b], ActivityState.ACTIVE, "T1B should be active")

    def test_parallel_nature_choice(self):
        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "(T1A ^[N1] T1B) || (T2A /[C2] T2B)",
            H: 0,
            IMPACTS: {"T1A": [0, 1], "T1B": [0, 2], "T2A": [0, 3], "T2B": [0, 4]},
            DURATIONS: {"T1A": [0, 1], "T1B": [0, 2], "T2A": [0, 3], "T2B": [0, 4]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {"N1": 0.6}, DELAYS: {"C2": 0}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "parallel_nature_eq_choice")

        p1 = Parallel(None, 0, 0)
        n1 = Nature(p1, 0, 1, "N1", 0.6)
        t1a = Task(p1, 0, 2, "T1A", [], 0)
        t1b = Task(p1, 1, 3, "T1B", [], 0)

        c2 = Choice(p1, 1, 4, "C2", 1)
        t2a = Task(p1, 0, 5, "T2A", [], 0)
        t2b = Task(p1, 1, 6, "T2B", [], 0)

        self.assertEqual(states.activityState[p1], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[p1], 0,
                         "P1 should be executed with time 0")
        self.assertEqual(states.activityState[n1], ActivityState.ACTIVE,
                         "N1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n1], 0,
                         "N1 should be executed with time 0")
        self.assertEqual(states.activityState[t1a], ActivityState.WAITING,
                         "T1A should be waiting")
        self.assertEqual(states.executed_time[t1a], 0,
                         "T1A never increases its executed time")
        self.assertEqual(states.activityState[t1b], ActivityState.WAITING,
                         "T1B should be waiting")
        self.assertEqual(states.executed_time[t1b], 0,
                         "T1B never increases its executed time")
        self.assertEqual(states.activityState[c2], ActivityState.ACTIVE,
                         "C2 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c2], 0,
                         "C2 should be executed with time 0")
        self.assertEqual(states.activityState[t2a], ActivityState.WAITING,
                         "T2A should be waiting")
        self.assertEqual(states.executed_time[t2a], 0,
                         "T2A never increases its executed time")
        self.assertEqual(states.activityState[t2b], ActivityState.WAITING,
                         "T2B should be waiting")
        self.assertEqual(states.executed_time[t2b], 0,
                         "T2B never increases its executed time")

        self.assertEqual(len(choices) + len(natures), 2, "There should be one nature and one choice")
        self.assertEqual(natures[0], n1, "The nature should be N1")
        self.assertEqual(choices[0], c2, "The choice should be c2")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 4, "There should be 4 decisions")
        self.assertEqual(multi_decisions[0][0], t1a, "The first decision should be (T1A, T2A)")
        self.assertEqual(multi_decisions[0][1], t2a, "The first decision should be (T1A, T2A)")

        self.assertEqual(multi_decisions[1][0], t1a, "The second decision should be (T1A, T2B)")
        self.assertEqual(multi_decisions[1][1], t2b, "The second decision should be (T1A, T2B)")

        self.assertEqual(multi_decisions[2][0], t1b, "The third decision should be (T1B, T2A)")
        self.assertEqual(multi_decisions[2][1], t2a, "The third decision should be (T1B, T2A)")

        self.assertEqual(multi_decisions[3][0], t1b, "The fourth decision should be (T1B, T2B)")
        self.assertEqual(multi_decisions[3][1], t2b, "The fourth decision should be (T1B, T2B)")


        self.assertEqual(len(multi_branches), 4, "There should be 4 branches")

        self.assertEqual(multi_branches[0].activityState[t1a], ActivityState.ACTIVE, "T1A should be active")
        self.assertEqual(multi_branches[0].activityState[t1b], ActivityState.WILL_NOT_BE_EXECUTED, "T1B should be will not be executed")
        self.assertEqual(multi_branches[0].activityState[t2a], ActivityState.ACTIVE, "T2A should be active")
        self.assertEqual(multi_branches[0].activityState[t2b], ActivityState.WILL_NOT_BE_EXECUTED, "T2B should be will not be executed")

        self.assertEqual(multi_branches[1].activityState[t1a], ActivityState.ACTIVE, "T1A should be active")
        self.assertEqual(multi_branches[1].activityState[t1b], ActivityState.WILL_NOT_BE_EXECUTED, "T1B should be will not be executed")
        self.assertEqual(multi_branches[1].activityState[t2a], ActivityState.WILL_NOT_BE_EXECUTED, "T2A should be will not be executed")
        self.assertEqual(multi_branches[1].activityState[t2b], ActivityState.ACTIVE, "T2B should be active")

        self.assertEqual(multi_branches[2].activityState[t1a], ActivityState.WILL_NOT_BE_EXECUTED, "T1A should be active")
        self.assertEqual(multi_branches[2].activityState[t1b], ActivityState.ACTIVE, "T1B should be will not be executed")
        self.assertEqual(multi_branches[2].activityState[t2a], ActivityState.ACTIVE, "T2A should be active")
        self.assertEqual(multi_branches[2].activityState[t2b], ActivityState.WILL_NOT_BE_EXECUTED, "T2B should be will not be executed")

        self.assertEqual(multi_branches[3].activityState[t1a], ActivityState.WILL_NOT_BE_EXECUTED, "T1A should be active")
        self.assertEqual(multi_branches[3].activityState[t1b], ActivityState.ACTIVE, "T1B should be will not be executed")
        self.assertEqual(multi_branches[3].activityState[t2a], ActivityState.WILL_NOT_BE_EXECUTED, "T2A should be will not be executed")
        self.assertEqual(multi_branches[3].activityState[t2b], ActivityState.ACTIVE, "T2B should be active")


        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "(T1A /[C1] T1B) || (T2A /[C2] T2B)",
            H: 0,
            IMPACTS: {"T1A": [0, 1], "T1B": [0, 2], "T2A": [0, 3], "T2B": [0, 4]},
            DURATIONS: {"T1A": [0, 1], "T1B": [0, 2], "T2A": [0, 3], "T2B": [0, 4]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {}, DELAYS: {"C1": 1, "C2": 2}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "parallel_choice_lt_choice")

        self.assertEqual(states.activityState[p1], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[p1], 1,
                         "P1 should be executed with time 1")
        self.assertEqual(states.activityState[n1], ActivityState.ACTIVE,
                         "C1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n1], 1,
                         "C1 should be executed with time 1")
        self.assertEqual(states.activityState[t1a], ActivityState.WAITING,
                         "T1A should be waiting")
        self.assertEqual(states.executed_time[t1a], 0,
                         "T1A never increases its executed time")
        self.assertEqual(states.activityState[t1b], ActivityState.WAITING,
                         "T1B should be waiting")
        self.assertEqual(states.executed_time[t1b], 0,
                         "T1B never increases its executed time")
        self.assertEqual(states.activityState[c2], ActivityState.ACTIVE,
                         "C2 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c2], 1,
                         "C2 should be executed with time 0")
        self.assertEqual(states.activityState[t2a], ActivityState.WAITING,
                         "T2A should be waiting")
        self.assertEqual(states.executed_time[t2a], 0,
                         "T2A never increases its executed time")
        self.assertEqual(states.activityState[t2b], ActivityState.WAITING,
                         "T2B should be waiting")
        self.assertEqual(states.executed_time[t2b], 0,
                         "T2B never increases its executed time")


        self.assertEqual(len(choices) + len(natures), 1, "There should be one choice")
        self.assertEqual(choices[0], n1, "The choice should be C1")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t1a, "The first decision should be T1A")
        self.assertEqual(multi_decisions[1][0], t1b, "The second decision should be T1B")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t1a], ActivityState.ACTIVE, "T1A should be active")
        self.assertEqual(multi_branches[0].activityState[t1b], ActivityState.WILL_NOT_BE_EXECUTED, "T1B should be waiting")

        self.assertEqual(multi_branches[1].activityState[t1a], ActivityState.WILL_NOT_BE_EXECUTED, "T1A should be waiting")
        self.assertEqual(multi_branches[1].activityState[t1b], ActivityState.ACTIVE, "T1B should be active")


    def test_parallel_choice_nature_nature(self):
        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "(T1A /[C1] T1B) || (T2A ^[N2] T2B) || (T3A ^[N3] T3B)",
            H: 0,
            IMPACTS: {"T1A": [0, 1], "T1B": [0, 2], "T2A": [0, 3], "T2B": [0, 4], "T3A": [0, 5], "T3B": [0, 6]},
            DURATIONS: {"T1A": [0, 1], "T1B": [0, 2], "T2A": [0, 3], "T2B": [0, 4], "T3A": [0, 5], "T3B": [0, 6]},
            IMPACTS_NAMES: ["cost", "hours"],
            PROBABILITIES: {"N2": 0.6, "N3": 0.7}, DELAYS: {"C1": 0}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "parallel_choice_eq_nature_eq_nature")


        p1 = Parallel(None, 0, 0)
        p2 = Parallel(p1, 0, 1)
        c1 = Choice(p1, 0, 2, "C1", 0)
        t1a = Task(p1, 0, 3, "T1A", [], 0)
        t1b = Task(p1, 1, 4, "T1B", [], 0)

        n2 = Nature(p1, 1, 5, "N2", 0.6)
        t2a = Task(p1, 0, 6, "T2A", [], 0)
        t2b = Task(p1, 1, 7, "T2B", [], 0)

        n3 = Nature(p1, 1, 8, "N3", 0.7)
        t3a = Task(p1, 0, 9, "T3A", [], 0)
        t3b = Task(p1, 1, 10, "T3B", [], 0)

        self.assertEqual(states.activityState[p1], ActivityState.ACTIVE,
                         "The root should be active")
        self.assertEqual(states.executed_time[p1], 0,
                         "P1 should be executed with time 0")
        self.assertEqual(states.activityState[p2], ActivityState.ACTIVE,
                         "P2 should be active")
        self.assertEqual(states.executed_time[p2], 0,
                         "P2 should be executed with time 0")
        self.assertEqual(states.activityState[c1], ActivityState.ACTIVE,
                         "C1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[c1], 0,
                         "C1 should be executed with time 0")
        self.assertEqual(states.activityState[t1a], ActivityState.WAITING,
                         "T1A should be waiting")
        self.assertEqual(states.executed_time[t1a], 0,
                         "T1A never increases its executed time")
        self.assertEqual(states.activityState[t1b], ActivityState.WAITING,
                         "T1B should be waiting")
        self.assertEqual(states.executed_time[t1b], 0,
                         "T1B never increases its executed time")
        self.assertEqual(states.activityState[n2], ActivityState.ACTIVE,
                         "N2 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n2], 0,
                         "N2 should be executed with time 0")
        self.assertEqual(states.activityState[t2a], ActivityState.WAITING,
                         "T2A should be waiting")
        self.assertEqual(states.executed_time[t2a], 0,
                         "T2A never increases its executed time")
        self.assertEqual(states.activityState[t2b], ActivityState.WAITING,
                         "T2B should be waiting")
        self.assertEqual(states.executed_time[t2b], 0,
                         "T2B never increases its executed time")
        self.assertEqual(states.activityState[n3], ActivityState.ACTIVE,
                         "N2 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n3], 0,
                         "N2 should be executed with time 0")
        self.assertEqual(states.activityState[t3a], ActivityState.WAITING,
                         "T3A should be waiting")
        self.assertEqual(states.executed_time[t3a], 0,
                         "T3A never increases its executed time")
        self.assertEqual(states.activityState[t3b], ActivityState.WAITING,
                         "T3B should be waiting")
        self.assertEqual(states.executed_time[t3b], 0,
                         "T3B never increases its executed time")


        self.assertEqual(len(choices) + len(natures), 3, "There should be one choice and two nature")
        self.assertEqual(choices[0], c1, "The choice should be C1")
        self.assertEqual(natures[0], n2, "The nature should be N2")
        self.assertEqual(natures[1], n3, "The nature should be N2")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 8, "There should be 8 decisions")
        self.assertEqual(multi_decisions[0][0], t1a, "The first decision should be (*T1A, T2A, T3A)")
        self.assertEqual(multi_decisions[0][1], t2a, "The first decision should be (T1A, *T2A, T3A)")
        self.assertEqual(multi_decisions[0][2], t3a, "The first decision should be (T1A, T2A, T*3A)")

        self.assertEqual(multi_decisions[1][0], t1a, "The second decision should be (*T1A, T2A, T3B)")
        self.assertEqual(multi_decisions[1][1], t2a, "The second decision should be (T1A, *T2A, T3B)")
        self.assertEqual(multi_decisions[1][2], t3b, "The second decision should be (T1A, T2A, *T3B)")

        self.assertEqual(multi_decisions[2][0], t1a, "The third decision should be (*T1A, T2B, T3A)")
        self.assertEqual(multi_decisions[2][1], t2b, "The third decision should be (T1A, *T2B, T3A)")
        self.assertEqual(multi_decisions[2][2], t3a, "The third decision should be (T1A, T2B, *T3A)")

        self.assertEqual(multi_decisions[3][0], t1a, "The fourth decision should be (*T1A, T2B, T3B)")
        self.assertEqual(multi_decisions[3][1], t2b, "The fourth decision should be (T1A, *T2B, T3B)")
        self.assertEqual(multi_decisions[3][2], t3b, "The fourth decision should be (T1A, T2B, *T3B)")

        self.assertEqual(multi_decisions[4][0], t1b, "The fifth decision should be (*T1B, T2A, T3A)")
        self.assertEqual(multi_decisions[4][1], t2a, "The fifth decision should be (T1B, *T2A, T3A)")
        self.assertEqual(multi_decisions[4][2], t3a, "The fifth decision should be (T1B, T2A, *T3A)")

        self.assertEqual(multi_decisions[5][0], t1b, "The sixth decision should be (*T1B, T2A, T3B)")
        self.assertEqual(multi_decisions[5][1], t2a, "The sixth decision should be (T1B, *T2A, T3B)")
        self.assertEqual(multi_decisions[5][2], t3b, "The sixth decision should be (T1B, T2A, *T3B)")

        self.assertEqual(multi_decisions[6][0], t1b, "The seventh decision should be (*T1B, T2B, T3A)")
        self.assertEqual(multi_decisions[6][1], t2b, "The seventh decision should be (T1B, *T2B, T3A)")
        self.assertEqual(multi_decisions[6][2], t3a, "The seventh decision should be (T1B, T2B, *T3A)")

        self.assertEqual(multi_decisions[7][0], t1b, "The eighth decision should be (*T1B, T2B, T3B)")
        self.assertEqual(multi_decisions[7][1], t2b, "The eighth decision should be (T1B, *T2B, T3B)")
        self.assertEqual(multi_decisions[7][2], t3b, "The eighth decision should be (T1B, T2B, *T3B)")


        self.assertEqual(len(multi_branches), 8, "There should be 8 branches")

        self.assertEqual(multi_branches[0].activityState[t1a], ActivityState.ACTIVE, "T1A should be active")
        self.assertEqual(multi_branches[0].activityState[t1b], ActivityState.WILL_NOT_BE_EXECUTED, "T1B should be will not be executed")
        self.assertEqual(multi_branches[0].activityState[t2a], ActivityState.ACTIVE, "T2A should be active")
        self.assertEqual(multi_branches[0].activityState[t2b], ActivityState.WILL_NOT_BE_EXECUTED, "T2B should be will not be executed")
        self.assertEqual(multi_branches[0].activityState[t3a], ActivityState.ACTIVE, "T3A should be active")
        self.assertEqual(multi_branches[0].activityState[t3b], ActivityState.WILL_NOT_BE_EXECUTED, "T3B should be will not be executed")

        self.assertEqual(multi_branches[1].activityState[t1a], ActivityState.ACTIVE, "T1A should be active")
        self.assertEqual(multi_branches[1].activityState[t1b], ActivityState.WILL_NOT_BE_EXECUTED, "T1B should be will not be executed")
        self.assertEqual(multi_branches[1].activityState[t2a], ActivityState.ACTIVE, "T2A should be active")
        self.assertEqual(multi_branches[1].activityState[t2b], ActivityState.WILL_NOT_BE_EXECUTED, "T2B should be will not be executed")
        self.assertEqual(multi_branches[1].activityState[t3a], ActivityState.WILL_NOT_BE_EXECUTED, "T3A should be will not be executed")
        self.assertEqual(multi_branches[1].activityState[t3b], ActivityState.ACTIVE, "T3B should be active")


        self.assertEqual(multi_branches[2].activityState[t1a], ActivityState.ACTIVE, "T1A should be active")
        self.assertEqual(multi_branches[2].activityState[t1b], ActivityState.WILL_NOT_BE_EXECUTED, "T1B should be will not be executed")
        self.assertEqual(multi_branches[2].activityState[t2a], ActivityState.WILL_NOT_BE_EXECUTED, "T2A should be will not be executed")
        self.assertEqual(multi_branches[2].activityState[t2b], ActivityState.ACTIVE, "T2B should be active")
        self.assertEqual(multi_branches[2].activityState[t3a], ActivityState.ACTIVE, "T3A should be active")
        self.assertEqual(multi_branches[2].activityState[t3b], ActivityState.WILL_NOT_BE_EXECUTED, "T3B should be will not be executed")

        self.assertEqual(multi_branches[3].activityState[t1a], ActivityState.ACTIVE, "T1A should be active")
        self.assertEqual(multi_branches[3].activityState[t1b], ActivityState.WILL_NOT_BE_EXECUTED, "T1B should be will not be executed")
        self.assertEqual(multi_branches[3].activityState[t2a], ActivityState.WILL_NOT_BE_EXECUTED, "T2A should be will not be executed")
        self.assertEqual(multi_branches[3].activityState[t2b], ActivityState.ACTIVE, "T2B should be active")
        self.assertEqual(multi_branches[3].activityState[t3a], ActivityState.WILL_NOT_BE_EXECUTED, "T3A should be will not be executed")
        self.assertEqual(multi_branches[3].activityState[t3b], ActivityState.ACTIVE, "T3B should be active")



        self.assertEqual(multi_branches[4].activityState[t1a], ActivityState.WILL_NOT_BE_EXECUTED, "T1A should be will not be executed")
        self.assertEqual(multi_branches[4].activityState[t1b], ActivityState.ACTIVE, "T1B should be active")
        self.assertEqual(multi_branches[4].activityState[t2a], ActivityState.ACTIVE, "T2A should be active")
        self.assertEqual(multi_branches[4].activityState[t2b], ActivityState.WILL_NOT_BE_EXECUTED, "T2B should be will not be executed")
        self.assertEqual(multi_branches[4].activityState[t3a], ActivityState.ACTIVE, "T3A should be active")
        self.assertEqual(multi_branches[4].activityState[t3b], ActivityState.WILL_NOT_BE_EXECUTED, "T3B should be will not be executed")

        self.assertEqual(multi_branches[5].activityState[t1a], ActivityState.WILL_NOT_BE_EXECUTED, "T1A should be will not be executed")
        self.assertEqual(multi_branches[5].activityState[t1b], ActivityState.ACTIVE, "T1B should be active")
        self.assertEqual(multi_branches[5].activityState[t2a], ActivityState.ACTIVE, "T2A should be active")
        self.assertEqual(multi_branches[5].activityState[t2b], ActivityState.WILL_NOT_BE_EXECUTED, "T2B should be will not be executed")
        self.assertEqual(multi_branches[5].activityState[t3a], ActivityState.WILL_NOT_BE_EXECUTED, "T3A should be will not be executed")
        self.assertEqual(multi_branches[5].activityState[t3b], ActivityState.ACTIVE, "T3B should be active")


        self.assertEqual(multi_branches[6].activityState[t1a], ActivityState.WILL_NOT_BE_EXECUTED, "T1A should be will not be executed")
        self.assertEqual(multi_branches[6].activityState[t1b], ActivityState.ACTIVE, "T1B should be active")
        self.assertEqual(multi_branches[6].activityState[t2a], ActivityState.WILL_NOT_BE_EXECUTED, "T2A should be will not be executed")
        self.assertEqual(multi_branches[6].activityState[t2b], ActivityState.ACTIVE, "T2B should be active")
        self.assertEqual(multi_branches[6].activityState[t3a], ActivityState.ACTIVE, "T3A should be active")
        self.assertEqual(multi_branches[6].activityState[t3b], ActivityState.WILL_NOT_BE_EXECUTED, "T3B should be will not be executed")

        self.assertEqual(multi_branches[7].activityState[t1a], ActivityState.WILL_NOT_BE_EXECUTED, "T1A should be will not be executed")
        self.assertEqual(multi_branches[7].activityState[t1b], ActivityState.ACTIVE, "T1B should be active")
        self.assertEqual(multi_branches[7].activityState[t2a], ActivityState.WILL_NOT_BE_EXECUTED, "T2A should be will not be executed")
        self.assertEqual(multi_branches[7].activityState[t2b], ActivityState.ACTIVE, "T2B should be active")
        self.assertEqual(multi_branches[7].activityState[t3a], ActivityState.WILL_NOT_BE_EXECUTED, "T3A should be will not be executed")
        self.assertEqual(multi_branches[7].activityState[t3b], ActivityState.ACTIVE, "T3B should be active")


    def test_parallel_sequential_nature(self):
        # 3 test, parallel: T1 = T2, T1 < T2, T1 > T2

        # T1 T2 ended and N1 start at the same time
        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "T1 || T2,(T3 ^ [N1] T4)",
            H: 0,
            IMPACTS: {"T1": [1, 2], "T2": [3, 4], "T3": [5, 6], "T4": [7, 8]},
            DURATIONS: {"T1": [0, 1], "T2": [0, 1], "T3": [0, 2], "T4": [0, 3]},
            IMPACTS_NAMES: ["a", "b"],
            PROBABILITIES: {"N1": 0.6}, DELAYS: {}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "parallel_sequential_nature")

        p1 = Parallel(None, 0, 0)
        t1 = Task(p1, 0, 1, "T1", [], 0)
        t2 = Task(p1, 0, 3, "T2", [], 0)
        n1 = Nature(p1, 1, 4, "N1", 0.6)
        t3 = Task(p1, 0, 5, "T3", [], 0)
        t4 = Task(p1, 1, 6, "T4", [], 0)

        self.assertEqual(states.activityState[p1], ActivityState.ACTIVE, "The root should be active")
        self.assertEqual(states.executed_time[p1], 1, "P1 should be executed with time 1")

        self.assertEqual(states.activityState[t1], ActivityState.COMPLETED_WITHOUT_PASSING_OVER, "T1 should be completed without passing over")
        self.assertEqual(states.executed_time[t1], 1, "T1 should be completed at time 0")

        self.assertEqual(states.activityState[t2], ActivityState.COMPLETED_WITHOUT_PASSING_OVER, "T2 should be completed without passing over")
        self.assertEqual(states.executed_time[t2], 1, "T2 should be completed at time 1")

        self.assertEqual(states.activityState[n1], ActivityState.ACTIVE, "N1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n1], 0, "N1 never increases its executed time")
        self.assertEqual(states.activityState[t3], ActivityState.WAITING, "T3 should be waiting")
        self.assertEqual(states.activityState[t4], ActivityState.WAITING, "T4 should be waiting")
        self.assertEqual(states.executed_time[t3], 0, "T3 never increases its executed time")
        self.assertEqual(states.executed_time[t4], 0, "T4 never increases its executed time")

        self.assertEqual(len(choices) + len(natures), 1, "There should be one nature")
        self.assertEqual(natures[0], n1, "The nature should be N1")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t3, "The first decision should be T3")
        self.assertEqual(multi_decisions[1][0], t4, "The second decision should be T4")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t3], ActivityState.ACTIVE, "T3 should be active")
        self.assertEqual(multi_branches[0].activityState[t4], ActivityState.WILL_NOT_BE_EXECUTED, "T4 should be waiting")

        self.assertEqual(multi_branches[1].activityState[t3], ActivityState.WILL_NOT_BE_EXECUTED, "T3 should be waiting")
        self.assertEqual(multi_branches[1].activityState[t4], ActivityState.ACTIVE, "T4 should be active")

        # T1 ended first
        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "T1 || T2,(T3 ^ [N1] T4)",
            H: 0,
            IMPACTS: {"T1": [1, 2], "T2": [3, 4], "T3": [5, 6], "T4": [7, 8]},
            DURATIONS: {"T1": [0, 1], "T2": [0, 2], "T3": [0, 2], "T4": [0, 3]},
            IMPACTS_NAMES: ["a", "b"],
            PROBABILITIES: {"N1": 0.6}, DELAYS: {}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "parallel_sequential_nature")

        self.assertEqual(states.activityState[p1], ActivityState.ACTIVE, "The root should be active")
        self.assertEqual(states.executed_time[p1], 2, "P1 should be executed with time 2")

        self.assertEqual(states.activityState[t1], ActivityState.COMPLETED, "T1 should be completed")
        self.assertEqual(states.executed_time[t1], 1, "T1 should be completed at time 0")

        self.assertEqual(states.activityState[t2], ActivityState.COMPLETED_WITHOUT_PASSING_OVER, "T2 should be completed without passing over")
        self.assertEqual(states.executed_time[t2], 2, "T2 should be completed at time 1")

        self.assertEqual(states.activityState[n1], ActivityState.ACTIVE, "N1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n1], 0, "N1 never increases its executed time")
        self.assertEqual(states.activityState[t3], ActivityState.WAITING, "T3 should be waiting")
        self.assertEqual(states.activityState[t4], ActivityState.WAITING, "T4 should be waiting")
        self.assertEqual(states.executed_time[t3], 0, "T3 never increases its executed time")
        self.assertEqual(states.executed_time[t4], 0, "T4 never increases its executed time")

        self.assertEqual(len(choices) + len(natures), 1, "There should be one nature")
        self.assertEqual(natures[0], n1, "The nature should be N1")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t3, "The first decision should be T3")
        self.assertEqual(multi_decisions[1][0], t4, "The second decision should be T4")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t3], ActivityState.ACTIVE, "T3 should be active")
        self.assertEqual(multi_branches[0].activityState[t4], ActivityState.WILL_NOT_BE_EXECUTED, "T4 should be waiting")

        self.assertEqual(multi_branches[1].activityState[t3], ActivityState.WILL_NOT_BE_EXECUTED, "T3 should be waiting")
        self.assertEqual(multi_branches[1].activityState[t4], ActivityState.ACTIVE, "T4 should be active")

        # T2 ended first
        parse_tree, pending_choice, pending_natures = test_create_parse_tree({
            EXPRESSION: "T1 || T2,(T3 ^ [N1] T4)",
            H: 0,
            IMPACTS: {"T1": [1, 2], "T2": [3, 4], "T3": [5, 6], "T4": [7, 8]},
            DURATIONS: {"T1": [0, 2], "T2": [0, 1], "T3": [0, 2], "T4": [0, 3]},
            IMPACTS_NAMES: ["a", "b"],
            PROBABILITIES: {"N1": 0.6}, DELAYS: {}, LOOP_PROBABILITY: {}, LOOP_ROUND: {}
        })
        states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(parse_tree, States(), pending_choice, pending_natures)
        self.info(parse_tree, states, "parallel_sequential_nature")

        self.assertEqual(states.activityState[p1], ActivityState.ACTIVE, "The root should be active")
        self.assertEqual(states.executed_time[p1], 1, "P1 should be executed with time 1")

        self.assertEqual(states.activityState[t1], ActivityState.ACTIVE, "T1 should be active")
        self.assertEqual(states.executed_time[t1], 1, "T1 should be completed at time 0")

        self.assertEqual(states.activityState[t2], ActivityState.COMPLETED_WITHOUT_PASSING_OVER, "T2 should be completed without passing over")
        self.assertEqual(states.executed_time[t2], 1, "T2 should be completed at time 1")

        self.assertEqual(states.activityState[n1], ActivityState.ACTIVE, "N1 should be active, with two waiting children")
        self.assertEqual(states.executed_time[n1], 0, "N1 never increases its executed time")
        self.assertEqual(states.activityState[t3], ActivityState.WAITING, "T3 should be waiting")
        self.assertEqual(states.activityState[t4], ActivityState.WAITING, "T4 should be waiting")
        self.assertEqual(states.executed_time[t3], 0, "T3 never increases its executed time")
        self.assertEqual(states.executed_time[t4], 0, "T4 never increases its executed time")

        self.assertEqual(len(choices) + len(natures), 1, "There should be one nature")
        self.assertEqual(natures[0], n1, "The nature should be N1")

        multi_decisions = []
        multi_branches = []
        for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
            multi_decisions.append(decisions)
            multi_branches.append(branch_states)

        self.assertEqual(len(multi_decisions), 2, "There should be two decisions")
        self.assertEqual(multi_decisions[0][0], t3, "The first decision should be T3")
        self.assertEqual(multi_decisions[1][0], t4, "The second decision should be T4")

        self.assertEqual(len(multi_branches), 2, "There should be two branches")
        self.assertEqual(multi_branches[0].activityState[t3], ActivityState.ACTIVE, "T3 should be active")
        self.assertEqual(multi_branches[0].activityState[t4], ActivityState.WILL_NOT_BE_EXECUTED, "T4 should be waiting")

        self.assertEqual(multi_branches[1].activityState[t3], ActivityState.WILL_NOT_BE_EXECUTED, "T3 should be waiting")
        self.assertEqual(multi_branches[1].activityState[t4], ActivityState.ACTIVE, "T4 should be active")


if __name__ == '__main__':
    unittest.main()


