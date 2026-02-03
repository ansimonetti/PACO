from src.paco.saturate_execution.next_state import next_state
from src.paco.saturate_execution.states import States, ActivityState
from src.paco.saturate_execution.step_to_saturation import steps_to_saturation
from src.paco.parser.parse_tree import ParseTree
from src.paco.parser.parse_node import ParseNode, Choice, Nature

def saturate_execution(region_tree: ParseTree, states: States, pending_choices:set, pending_natures:set) -> (States, bool, list[ParseNode], list[ParseNode]):
	while states.activityState[region_tree.root] < ActivityState.COMPLETED:
		#print("step_to_saturation:")
		#print("start:", states_info(states))

		k = steps_to_saturation(region_tree.root, states)
		#print('step_to_saturation:k:', k, states_info(states))

		updatedStates, k = next_state(region_tree.root, states, k)
		states.update(updatedStates)

		#print('next_state:k:', k, states_info(states))
		if k > 0:
			raise Exception("StepsException" + str(k))

		choices, natures = [], []
		node: ParseNode
		for node in list(states.activityState.keys()):
			if (isinstance(node, Choice)
					and states.activityState[node] == ActivityState.ACTIVE
					and states.executed_time[node] == node.max_delay
					and states.activityState[node.children[0]] == ActivityState.WAITING
					and states.activityState[node.children[1]] == ActivityState.WAITING):
				choices.append(node)

			if (isinstance(node, Nature)
					and states.activityState[node] == ActivityState.ACTIVE
					and states.activityState[node.children[0]] == ActivityState.WAITING
					and states.activityState[node.children[1]] == ActivityState.WAITING):
				natures.append(node)

		pending_choices = pending_choices - set(choices)
		pending_natures = pending_natures - set(natures)
		if len(choices) > 0 or len(natures) > 0:
			return states, False, choices, natures, pending_choices, pending_natures

	return states, True, [], [], pending_choices, pending_natures
