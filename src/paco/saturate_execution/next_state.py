import math
from src.paco.parser.parse_tree import ParseTree
from src.paco.parser.parse_node import ParseNode, Sequential, Parallel, ExclusiveGateway, Nature, Task
from src.paco.saturate_execution.states import States, ActivityState, node_info


def next_state(root: ParseNode, states: States, k: int) -> (States, int):
	#print(f"next_state: " + node_info(root, states))

	if isinstance(root, Task):
		#print("next_state:Task: " + node_info(root, states))

		remaining_time = root.duration - states.executed_time[root]
		if remaining_time >= k:
			#print(f"next_state:Task:remaining_time >= k: {remaining_time} >= {k}")
			return (States(root,
						   ActivityState.ACTIVE if remaining_time > k else ActivityState.COMPLETED_WITHOUT_PASSING_OVER,
						   states.executed_time[root] + k),
					0)

		states.activityState[root] = ActivityState.COMPLETED
		#print(f"next_state:Task:remaining_time < k: {remaining_time} < {k}: ActivityCompleted!")
		return (States(root, ActivityState.COMPLETED, root.duration),
				states.executed_time[root] + k - root.duration)

	sx_child = root.children[0]
	dx_child = root.children[1]

	if isinstance(root, ExclusiveGateway):
		childSx = states.activityState[sx_child] >= ActivityState.ACTIVE
		if childSx or states.activityState[dx_child] >= ActivityState.ACTIVE:
			selectedChild = sx_child if childSx else dx_child
			selectedStates, selectedK = next_state(selectedChild, states, k)

			selectedStates.activityState[root] = selectedStates.activityState[selectedChild]
			selectedStates.executed_time[root] = states.executed_time[root] + k - selectedK
			return selectedStates, selectedK

		if isinstance(root, Nature):
			if k > 0:
				raise Exception("next_state:ExceedingStepsException:Natural")
			#print(f"next_state:Natural:k: 0")
			return States(root, ActivityState.ACTIVE, 0), 0
		else:
			if states.executed_time[root] + k > root.max_delay:
				raise Exception("next_state:ExceedingStepsException:Choice")

			#print(f"next_state:Choice:remaining_time == k: k={k}")
			return States(root, ActivityState.ACTIVE, states.executed_time[root] + k), 0

	if isinstance(root, Sequential):
		#print("next_state:Sequential: " + node_info(root, states))
		leftStates = States()
		#leftStates = States(sx_child, ActivityState.COMPLETED, states.executed_time[sx_child]) #Not needed
		leftK = k
		if states.activityState[sx_child] != ActivityState.COMPLETED:
			leftStates, leftK = next_state(sx_child, states, k)

			#print(f"next_state:Sequential: {node_info(root, states)} leftK: {leftK}")
			#print("next_state:Sequential:LeftStates:")
			#print_states(leftStates)

			if leftStates.activityState[sx_child] == ActivityState.ACTIVE:
				leftStates.activityState[root] = ActivityState.ACTIVE
				leftStates.executed_time[root] = leftStates.executed_time[sx_child]
				return leftStates, leftK

		rightStates, rightK = next_state(dx_child, states, leftK)
		#print(f"next_state:Sequential: {node_info(root, states)} rightK: {rightK}")
		#print("Sequential:right " + node_info(dx_child, states))
		#print(f"Sequential:right:{rightCl} {rightK}")

		leftStates.update(rightStates)
		leftStates.activityState[root] = rightStates.activityState[dx_child]
		leftStates.executed_time[root] = states.executed_time[root] + k - rightK

		return leftStates, rightK

	if isinstance(root, Parallel):
		#print("next_state:Parallel: " + node_info(root, states))
		leftK = rightK = math.inf
		#leftStates = States()
		#rightStates = States()
		leftStates = States(sx_child, ActivityState.COMPLETED, states.executed_time[sx_child])
		rightStates = States(dx_child, ActivityState.COMPLETED, states.executed_time[dx_child])

		#print("next_state:Parallel:LeftCheck ")# + node_info(sx_child, states))
		if states.activityState[sx_child] != ActivityState.COMPLETED:
			#print("next_state:Parallel:Left")
			leftStates, leftK = next_state(sx_child, states, k)
		#print("next_state:Parallel:LeftStates:")
		#print_states(leftStates)

		#print("next_state:Parallel:RightCheck ")# + node_info(dx_child, states))
		if states.activityState[dx_child] != ActivityState.COMPLETED:
			#print("next_state:Parallel:Right")
			rightStates, rightK = next_state(dx_child, states, k)
		#print("next_state:Parallel:RightStates:")
		#print_states(rightStates)

		if (leftStates.activityState[sx_child] == ActivityState.ACTIVE or
				rightStates.activityState[dx_child] == ActivityState.ACTIVE):

			status = ActivityState.ACTIVE
		elif (leftStates.activityState[sx_child] == ActivityState.COMPLETED and
			  rightStates.activityState[dx_child] == ActivityState.COMPLETED):

			status = ActivityState.COMPLETED
		else:
			status = ActivityState.COMPLETED_WITHOUT_PASSING_OVER

		leftStates.update(rightStates)
		leftStates.activityState[root] = status
		leftStates.executed_time[root] = states.executed_time[root] + k - min(leftK, rightK)

		return leftStates, min(leftK, rightK)

	raise Exception(f"next_state:invalid type: ", root)
