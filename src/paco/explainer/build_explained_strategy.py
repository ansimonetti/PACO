from datetime import datetime
from src.paco.explainer.explain_strategy import explain_strategy
from src.paco.explainer.full_strategy import full_strategy
from src.paco.explainer.explanation_type import ExplanationType
from src.paco.parser.parse_tree import ParseTree
from src.paco.parser.parse_node import ParseNode
from src.paco.execution_tree.execution_tree import ExecutionTree

def build_explained_strategy(parse_tree:ParseTree, strategy: dict[ParseNode, dict[ParseNode, set[ExecutionTree]]], type_strategy: ExplanationType, impacts_names: list,  pending_choices:set, pending_natures:set, debug=False):
    times = {}

    #print(f'{datetime.now()} Explain Strategy: ')
    t = datetime.now()
    worst_type_strategy, bdds = explain_strategy(parse_tree, strategy, impacts_names, type_strategy, debug)
    t1 = datetime.now()
    time_explain_strategy = (t1 - t).total_seconds()*1000
    #print(f"{t1} Explain Strategy:completed: {time_explain_strategy} ms")
    times["time_explain_strategy"] = time_explain_strategy

    s = f": {worst_type_strategy}"
    if type_strategy == ExplanationType.HYBRID:
        s = f"with worst type of choice{s}"
    #print(f"{t1} Strategy {s}\nname\t type\t\n"+ "".join(f"{choice.name}:\t{bdd.typeStrategy}\n" for choice, bdd in bdds.items()))

    #print(f'{t1} StrategyTree: ')
    t = datetime.now()
    strategy_tree, children, expected_impacts, expected_time, pending_choices, pending_natures, _ = full_strategy(parse_tree, bdds, len(impacts_names), pending_choices, pending_natures)
    t1 = datetime.now()
    strategy_tree_time = (t1 - t).total_seconds()*1000
    #print(f"{t1} StrategyTree:completed: {strategy_tree_time} ms\n")
    times["strategy_tree_time"] = strategy_tree_time

    #print(f"Strategy Expected Impacts: {expected_impacts}\nStrategy Expected Time: {expected_time}")
    if debug:
        strategy_tree.save_dot(
            state=True, executed_time=True, diff=False)

    return strategy_tree, expected_impacts, expected_time, bdds, times