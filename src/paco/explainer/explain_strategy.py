import numpy as np
from src.paco.explainer.bdd.bdd import Bdd
from src.paco.explainer.explanation_type import current_impacts, decision_based, ExplanationType
from src.paco.parser.parse_tree import ParseTree
from src.paco.parser.parse_node import ParseNode
from src.paco.execution_tree.execution_tree import ExecutionTree


def explain_choice(choice:ParseNode, decisions:list[ParseNode], impacts:list[np.ndarray], labels:list, features_names:list, typeStrategy:ExplanationType, debug=False) -> Bdd:
	if len(decisions) == 0:
		raise Exception(f"explain_choice:Choice {choice.name} has no decisions")
	elif len(decisions) > 2:
		raise Exception(f"explain_choice:Choice {choice.name} has more than 2 decisions")

	is_unavoidable_decision = len(decisions) == 1
	if is_unavoidable_decision:
		decisions.append(None)

	bdd = Bdd(choice, decisions[0], decisions[1], typeStrategy,
			  impacts=impacts, labels=labels, features_names=features_names)

	is_separable = bdd.build(debug=debug) #Debug write on files
	if not is_separable:
		return None

	if debug:
		bdd.save_bdd()

	return bdd


def explain_strategy_full(region_tree: ParseTree, strategy: dict[ParseNode, dict[ParseNode, set[ExecutionTree]]], impacts_names: list[str], typeStrategy: ExplanationType = ExplanationType.CURRENT_IMPACTS, debug=False) -> (ExplanationType, dict[ParseNode, Bdd]):
	bdds = dict[ParseNode, Bdd]()
	for choice, decisions_taken in strategy.items():
		#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer:")
		features_names = impacts_names

		if typeStrategy == ExplanationType.CURRENT_IMPACTS:
			vectors, labels = current_impacts(decisions_taken)
		elif typeStrategy == ExplanationType.DECISION_BASED:
			features_names, vectors, labels = decision_based(region_tree, decisions_taken)
		else:
			raise Exception(f"Choice {choice.name} is impossible to explain")

		bdd = explain_choice(choice, list(decisions_taken.keys()), vectors, labels, features_names, typeStrategy, debug)

		if bdd is None:
			#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: failed")
			return explain_strategy(region_tree, strategy, impacts_names, ExplanationType(typeStrategy + 1))

		bdds[choice] = bdd
		#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: done")

	return typeStrategy, bdds


def explain_strategy_hybrid(region_tree: ParseTree, strategy: dict[ParseNode, dict[ParseNode, set[ExecutionTree]]], impacts_names: list[str], debug=False) -> (ExplanationType, dict[ParseNode, Bdd]):
	bdds = dict[ParseNode, Bdd]()

	worstType = ExplanationType.CURRENT_IMPACTS
	for choice, decisions_taken in strategy.items():
		#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer:")
		features_names = impacts_names
		typeStrategy = ExplanationType.CURRENT_IMPACTS
		bdd = None

		if typeStrategy == ExplanationType.CURRENT_IMPACTS:
			vectors, labels = current_impacts(decisions_taken)
			bdd = explain_choice(choice, list(decisions_taken.keys()), vectors, labels, features_names, typeStrategy, debug)
			if bdd is None:
				#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: failed")
				typeStrategy = ExplanationType(typeStrategy + 1)

		if typeStrategy == ExplanationType.DECISION_BASED:
			features_names, vectors, labels = decision_based(region_tree, decisions_taken)
			bdd = explain_choice(choice, list(decisions_taken.keys()), vectors, labels, features_names, typeStrategy, debug)
			if bdd is None:
				raise Exception(f"Choice {choice.name} is impossible to explain")

		bdds[choice] = bdd
		#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: done")

		if worstType < typeStrategy:
			worstType = typeStrategy

	return worstType, bdds


def explain_strategy(region_tree: ParseTree, strategy: dict[ParseNode, dict[ParseNode, set[ExecutionTree]]], impacts_names: list[str], typeStrategy: ExplanationType = ExplanationType.HYBRID, debug=False) -> (ExplanationType, dict[ParseNode, Bdd]):
	if typeStrategy == ExplanationType.HYBRID:
		return explain_strategy_hybrid(region_tree, strategy, impacts_names, debug)

	return explain_strategy_full(region_tree, strategy, impacts_names, typeStrategy, debug)


