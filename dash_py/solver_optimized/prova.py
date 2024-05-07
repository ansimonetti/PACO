from solver.tree_lib import CTree, CNode

state = {
    'task1': [0, 5], #  0 = state 5 = durata
    'task2': [0, 0],
    'task3': [0, 0],
}
def stepSaturation(tree: CTree, state = {}):
    root = tree.root
    if root.type == 'task':
        # se task mi fermo # TODO CHECK
        return 0
    elif root.type == 'sequential':
        if state[root.childrens[0]][0] == 1:
            # se a sx già andato vado a dx
            return stepSaturation(CTree(root.childrens[1]), state)
        else:
            # altrimenti vado a sx
            return stepSaturation(CTree(root.childrens[0]), state)
    elif root.type == 'parallel':
        # TODO check left messo male
        # dur_left = 10000000000000
        # dur_right = 10000000000000 
        # if state[left][0] < 2 and state[left][0] >= 0:
        #     dur_left = stepSaturation(CTree(root.childrens[0]), state)
        # if state[right][0] < 2 and state[right][0] >= 0:
        #     dur_right = stepSaturation(CTree(root.childrens[1]), state)
        # return min(dur_left, dur_right)
        return stepSaturation(CTree(root.childrens[0]), state), stepSaturation(CTree(root.childrens[1]), state)
    elif root.type == 'natural':
        left = stepSaturation(CTree(root.childrens[0]), state)
        right = stepSaturation(CTree(root.childrens[1]), state)
        if state[left][0] == 1:
            # se sto facendo ramo sx vado avanti
            return stepSaturation(CTree(root.childrens[0]), state)
        if state[right][0] == 1:
            # se sto facendo ramo dx vado avanti
            return stepSaturation(CTree(root.childrens[1]), state)
        else:
            return 0
    elif root.type == 'choice':
        left = stepSaturation(CTree(root.childrens[0]), state)
        right = stepSaturation(CTree(root.childrens[1]), state)
        if state[left][0] == 1:
            # se sto facendo ramo sx vado avanti
            return stepSaturation(CTree(root.childrens[0]), state)
        if state[right][0] == 1:
            # se sto facendo ramo dx vado avanti
            return stepSaturation(CTree(root.childrens[1]), state)
        else:
            return 0 # TODO CHECK
    