import copy
from src.paco.parser.parse_tree import ParseTree
from src.paco.parser.parse_node import ParseNode
from src.paco.saturate_execution.create_branches import create_branches
from src.paco.saturate_execution.next_state import next_state
from src.paco.saturate_execution.states import States, ActivityState, states_info
from src.paco.saturate_execution.step_to_saturation import steps_to_saturation

# Saturation of the execution tree activating decisions nodes
def saturate_execution_decisions(region_tree: ParseTree, states: States, pending_choices:set, pending_natures:set) -> (States, tuple[ParseNode], dict[tuple[ParseNode], (States,set,set)]):
	branches = dict()
	choices = tuple()
	natures = tuple()

	states = copy.deepcopy(states)
	while len(choices) + len(natures) == 0 and states.activityState[region_tree.root] < ActivityState.COMPLETED:
		#print("step_to_saturation:")
		#print("start:", states_info(states))

		k = steps_to_saturation(region_tree.root, states)
		#print('step_to_saturation:k:', k, states_info(states))

		updatedStates, k = next_state(region_tree.root, states, k)
		states.update(updatedStates)

		#print('next_state:k:', k, states_info(states))
		if k > 0:
			raise Exception("saturate_execution:StepsException" + str(k))

		choices, natures, pending_choices, pending_natures, branches = create_branches(states, pending_choices, pending_natures)

	#if len(branches) > 0:
		#print("create_branches:", states_info(states))

	#print("Branches:" + str(len(branches)))
	#print("Root activity state: ", states.activityState[region_tree.root], states_info(states))

	return states, choices, natures, pending_choices, pending_natures, branches
