from tree_lib import CTree
import numpy as np
from aalpy.base import SUL

MAX_DELAY = 1

FAILED = False
ADMITTED = True

COMPLETE = 1
CHAR_ACCEPTED = 0
INVALID_CHAR = -1

class BluePrint:
    # custom class for representing BluePrints
    # the id is the BPM id of the node that triggers the BluePrint, i.e. the hierarchically most important one
    # the variables are the ids of the childrens of the trigger node
    # the sequences are sequences of values that could be assigned to variables
    ## the allowed values are:
    ### -1 for a region that won't execute
    ### 0 for a region that hasn't executed yet, ma can execute in the future
    ### 1 for a region that is on execution
    ### 2 for a region that has already completely executed
    # the pumping point are the instants in which the execution could wait

    def __init__(self, id: int, variables: list[int], sequences: list[list[int]], pumping_points: list[int] = []) -> None:
        self.id = id
        self.variables = variables
        self.sequences = sequences
        self.pumping_points = pumping_points
        self.sequence_length = len(sequences[0])

    def __str__(self) -> str:
        string_to_be_returned = str(str(self.id) + " " + str(self.variables) + " " + str(self.sequences) + " " + str(self.pumping_points))
        return string_to_be_returned
    
    def copy(self):
        return BluePrint(self.id, self.variables.copy(), self.sequences.copy(), self.pumping_points.copy())

class ViewPoint:
    # custom class for representing a ViewPoint, a "screenshot" of a Blueprint
    # the id corresponds to the id of the BluePrint to which the ViewPoint refers
    # the index represents the instant in which we are currently located inside a BluePrint

    def __init__(self, blueprint: BluePrint, index: int = -1) -> None:
        self.id = blueprint.id
        self.blueprint = blueprint
        self.index = index

    def reset(self):
        self.index = -1

    def step(self) -> bool:
        # this method makes a step inside the blueprint, and returns True if it did manage to do it, False otherwise
        if self.index == self.blueprint.sequence_length-1:
            return False
        else:
            self.index = self.index + 1
            return True
        
    def step_back(self) -> bool:
        # this method makes a step back inside the blueprint, and returns True if it did manage to do it, False otherwise
        if self.index == -1:
            return False
        else:
            self.index = self.index - 1
            return True
        
    def copy(self):
        return ViewPoint(self.blueprint.copy(), self.index)

class ViewPointList:
    # custom class for representing a ViewPoint list, with some useful additional structures

    def __init__(self, view_point_list: list[ViewPoint]) -> None:
        self.view_point_list = view_point_list
        self.ACTIVE_VP = len(self.view_point_list) # number of viewpoints that hadn't failed yet
        self.ACTIVE_VP_INDICES = list(range(self.ACTIVE_VP)) # list of indices of viewpoints that hadn't failed yet

    def reset(self):
        self.ACTIVE_VP = len(self.view_point_list)
        self.ACTIVE_VP_INDICES = list(range(self.ACTIVE_VP))
        for vp in self.view_point_list:
            vp.reset()

    def copy(self):
        tmp_view_point_list = [vp.copy() for vp in self.view_point_list]
        tmp_view_point = ViewPointList(tmp_view_point_list)
        tmp_view_point.ACTIVE_VP = self.ACTIVE_VP
        tmp_view_point.ACTIVE_VP_INDICES = self.ACTIVE_VP_INDICES.copy()
        return tmp_view_point

class VPChecker(SUL):
    TASK = 0
    CHOICE = 1
    NATURAL = 2
    SEQUENTIAL = 3
    PARALLEL = 4

    def __init__(self, bpmTree: CTree, number_of_nodes: int) -> None:
        super().__init__()
        self.number_of_nodes = number_of_nodes
        self.FAILED = False
        starting_alphabet = [[1]+[None for _ in range(number_of_nodes-1)], [2]+[None for _ in range(number_of_nodes-1)]]
        self.VPDict, accepted_alphabet_raw = self.generateViewPointsFromBPMTree(bpmTree, accepted_alphabet=starting_alphabet)
        self.accepted_alphabet = [tuple(c) for c in accepted_alphabet_raw]
        self.types = [-1 for _ in range(number_of_nodes)]
        self.childrens = [None for _ in range(number_of_nodes)]
        self.task_dict = {}
        self.nature_dict = {}
        self.generateAdditionalData(bpmTree)
        
    def generateViewPointsFromBPMTree(self, bpmTree: CTree, starting_dictionary: dict[int,ViewPointList] = {}, accepted_alphabet = []) -> tuple[dict[int,ViewPointList], list[list[int]]]:
        view_points_list: list[ViewPoint] = []
        general_view_points_list: list[ViewPoint] = []

        root = bpmTree.root
        id = root.id
        if id == 0: #adding the general viewpoint
            general_view_points_list.append(ViewPoint(BluePrint(id, [id], [[1]])))
            general_view_points_list.append(ViewPoint(BluePrint(id, [id], [[1, 1]], [1])))
            general_view_points_list.append(ViewPoint(BluePrint(id, [id], [[1, 1, 2]], [1])))
            general_view_points_list.append(ViewPoint(BluePrint(id, [id], [[1, 2]])))
            general_view_points_list.append(ViewPoint(BluePrint(id, [id], [[1, 1, 2, 2]], [1, 3])))
            general_view_points_list.append(ViewPoint(BluePrint(id, [id], [[1, 2, 2]], [2])))
            self.VPGeneral = ViewPointList(general_view_points_list)
        if root.type == 'task':
            duration = root.duration
            ones = [1 for i in range(duration)]
            
            # execution
            view_points_list.append(ViewPoint(BluePrint(id, [id], [ones])))
            # not yet executed - execution
            view_points_list.append(ViewPoint(BluePrint(id, [id], [[0] + ones])))
            view_points_list.append(ViewPoint(BluePrint(id, [id], [[0, 0] + ones], [1])))
            # execution - already executed
            view_points_list.append(ViewPoint(BluePrint(id, [id], [ones + [2]])))
            view_points_list.append(ViewPoint(BluePrint(id, [id], [ones + [2, 2]], [duration + 1])))
            # not yet executed - execution - already executed
            view_points_list.append(ViewPoint(BluePrint(id, [id], [[0] + ones + [2]])))
            view_points_list.append(ViewPoint(BluePrint(id, [id], [[0, 0] + ones + [2]], [1])))
            view_points_list.append(ViewPoint(BluePrint(id, [id], [[0] + ones + [2, 2]], [duration + 2])))
            view_points_list.append(ViewPoint(BluePrint(id, [id], [[0, 0] + ones + [2, 2]], [1, duration + 3])))
            # never executed
            view_points_list.append(ViewPoint(BluePrint(id, [id], [[-1]])))
            view_points_list.append(ViewPoint(BluePrint(id, [id], [[-1, -1]], [1])))
            # not yet executed - never executed
            view_points_list.append(ViewPoint(BluePrint(id, [id], [[0, -1]])))
            view_points_list.append(ViewPoint(BluePrint(id, [id], [[0, 0, -1]], [1])))
            view_points_list.append(ViewPoint(BluePrint(id, [id], [[0, -1, -1]], [2])))
            view_points_list.append(ViewPoint(BluePrint(id, [id], [[0, 0, -1, -1]], [1, 3])))
            starting_dictionary[id] = ViewPointList(view_points_list)
        elif root.type == 'sequential':
            id_left_child = root.childrens[0].root.id
            id_right_child = root.childrens[1].root.id

            #updating accepted alphabet
            new_accepted_alphabet = []
            for ch in accepted_alphabet:
                if ch[id] == -1 or ch[id] == 0 or ch[id] == 2:
                    ch[id_left_child] = ch[id]
                    ch[id_right_child] = ch[id]
                    new_accepted_alphabet.append(ch.copy())
                elif ch[id] == 1:
                    for alt in [[1,0], [2,1]]:
                        ch[id_left_child] = alt[0]
                        ch[id_right_child] = alt[1]
                        new_accepted_alphabet.append(ch.copy())
            accepted_alphabet = new_accepted_alphabet
                    
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 2], [0, 1]])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 1, 2], [0, 0, 1]], [1])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 2, 2], [0, 1, 1]], [2])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 1, 2, 2], [0, 0, 1, 1]], [1, 3])))
            # with short and long wait with value = 2 at the end
            additional_vp_list = []
            for vp in view_points_list:
                seq_with_short_wait = [s + [2] for s in vp.blueprint.sequences]
                seq_with_long_wait = [s + [2, 2] for s in vp.blueprint.sequences]
                pp_for_long_wait  = vp.blueprint.pumping_points + [len(seq_with_long_wait[0])-1]
                additional_vp_list.append(ViewPoint(BluePrint(id, vp.blueprint.variables, seq_with_short_wait, vp.blueprint.pumping_points)))
                additional_vp_list.append(ViewPoint(BluePrint(id, vp.blueprint.variables, seq_with_long_wait, pp_for_long_wait)))
            view_points_list += additional_vp_list

            starting_dictionary[id] = ViewPointList(view_points_list)
            starting_dictionary, accepted_alphabet = self.generateViewPointsFromBPMTree(root.childrens[0], starting_dictionary=starting_dictionary, accepted_alphabet=accepted_alphabet)
            starting_dictionary, accepted_alphabet = self.generateViewPointsFromBPMTree(root.childrens[1], starting_dictionary=starting_dictionary, accepted_alphabet=accepted_alphabet)
        elif root.type == 'natural':
            id_left_child = root.childrens[0].root.id
            id_right_child = root.childrens[1].root.id

            #updating accepted alphabet
            new_accepted_alphabet = []
            for ch in accepted_alphabet:
                if ch[id] == -1 or ch[id] == 0:
                    ch[id_left_child] = ch[id]
                    ch[id_right_child] = ch[id]
                    new_accepted_alphabet.append(ch.copy())
                elif ch[id] == 2:
                    for alt in [[2,-1], [-1,2]]:
                        ch[id_left_child] = alt[0]
                        ch[id_right_child] = alt[1]
                        new_accepted_alphabet.append(ch.copy())
                elif ch[id] == 1:
                    for alt in [[1,-1], [-1,1]]:
                        ch[id_left_child] = alt[0]
                        ch[id_right_child] = alt[1]
                        new_accepted_alphabet.append(ch.copy())
            accepted_alphabet = new_accepted_alphabet

            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1], [-1]])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[-1], [1]])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 1], [-1, -1]], [1])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[-1, -1], [1, 1]], [1])))
            # with short and long wait with value = 2 at the end
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 2], [-1, -1]])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[-1, -1], [1, 2]])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 1, 2], [-1, -1, -1]], [1])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[-1, -1, -1], [1, 1, 2]], [1])))

            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 2, 2], [-1, -1, -1]], [2])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[-1, -1, -1], [1, 2, 2]], [2])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 1, 2, 2], [-1, -1, -1, -1]], [1, 3])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[-1, -1, -1, -1], [1, 1, 2, 2]], [1, 3])))

            starting_dictionary[id] = ViewPointList(view_points_list)
            starting_dictionary, accepted_alphabet = self.generateViewPointsFromBPMTree(root.childrens[0], starting_dictionary=starting_dictionary, accepted_alphabet=accepted_alphabet)
            starting_dictionary, accepted_alphabet = self.generateViewPointsFromBPMTree(root.childrens[1], starting_dictionary=starting_dictionary, accepted_alphabet=accepted_alphabet)
        elif root.type == 'choice':
            max_delay = root.max_delay if root.max_delay != np.Inf else MAX_DELAY
            id_left_child = root.childrens[0].root.id
            id_right_child = root.childrens[1].root.id
            zeros = [0 for i in range(int(max_delay))]

            #updating accepted alphabet
            new_accepted_alphabet = []
            for ch in accepted_alphabet:
                if ch[id] == -1 or ch[id] == 0:
                    ch[id_left_child] = ch[id]
                    ch[id_right_child] = ch[id]
                    new_accepted_alphabet.append(ch.copy())
                elif ch[id] == 2:
                    for alt in [[2,-1], [-1,2]]:
                        ch[id_left_child] = alt[0]
                        ch[id_right_child] = alt[1]
                        new_accepted_alphabet.append(ch.copy())
                elif ch[id] == 1:
                    for alt in [[0,0], [1,-1], [-1,1]]:
                        ch[id_left_child] = alt[0]
                        ch[id_right_child] = alt[1]
                        new_accepted_alphabet.append(ch.copy())
            accepted_alphabet = new_accepted_alphabet

            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [zeros + [1], zeros + [-1]])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [zeros + [-1], zeros + [1]])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [zeros + [1, 1], zeros + [-1, -1]], [max_delay + 1])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [zeros + [-1, -1], zeros + [1, 1]], [max_delay + 1])))
            # with short and long wait with value = 2 at the end
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [zeros + [1, 2], zeros + [-1, -1]])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [zeros + [-1, -1], zeros + [1, 2]])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [zeros + [1, 1, 2], zeros + [-1, -1, -1]], [max_delay + 1])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [zeros + [-1, -1, -1], zeros + [1, 1, 2]], [max_delay + 1])))

            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [zeros + [1, 2, 2], zeros + [-1, -1, -1]], [max_delay + 2])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [zeros + [-1, -1, -1], zeros + [1, 2, 2]], [max_delay + 2])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [zeros + [1, 1, 2, 2], zeros + [-1, -1, -1, -1]], [max_delay + 1, max_delay + 3])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [zeros + [-1, -1, -1, -1], zeros + [1, 1, 2, 2]], [max_delay + 1, max_delay + 3])))
            starting_dictionary[id] = ViewPointList(view_points_list)
            starting_dictionary, accepted_alphabet = self.generateViewPointsFromBPMTree(root.childrens[0], starting_dictionary=starting_dictionary, accepted_alphabet=accepted_alphabet)
            starting_dictionary, accepted_alphabet = self.generateViewPointsFromBPMTree(root.childrens[1], starting_dictionary=starting_dictionary, accepted_alphabet=accepted_alphabet)
        elif root.type == 'parallel':
            id_left_child = root.childrens[0].root.id
            id_right_child = root.childrens[1].root.id

            #updating accepted alphabet
            new_accepted_alphabet = []
            for ch in accepted_alphabet:
                if ch[id] == -1 or ch[id] == 0 or ch[id] == 2:
                    ch[id_left_child] = ch[id]
                    ch[id_right_child] = ch[id]
                    new_accepted_alphabet.append(ch.copy())
                elif ch[id] == 1:
                    for alt in [[1,0], [0,1], [1,1], [2,1], [1,2]]:
                        ch[id_left_child] = alt[0]
                        ch[id_right_child] = alt[1]
                        new_accepted_alphabet.append(ch.copy())
            accepted_alphabet = new_accepted_alphabet

            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1], [1]])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 1], [1, 1]], [1])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 2], [1, 1]])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 1], [1, 2]])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 1, 2], [1, 1, 1]], [1])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 1, 1], [1, 1, 2]], [1])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 2, 2], [1, 1, 1]], [2])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 1, 1], [1, 2, 2]], [2])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 1, 2, 2], [1, 1, 1, 1]], [1, 3])))
            view_points_list.append(ViewPoint(BluePrint(id, [id_left_child, id_right_child], [[1, 1, 1, 1], [1, 1, 2, 2]], [1, 3])))
            # with short and long wait with value = 2 at the end
            additional_vp_list = []
            for vp in view_points_list:
                seq_with_short_wait = [s + [2] for s in vp.blueprint.sequences]
                seq_with_long_wait = [s + [2, 2] for s in vp.blueprint.sequences]
                pp_for_long_wait  = vp.blueprint.pumping_points + [len(seq_with_long_wait[0])-1]
                additional_vp_list.append(ViewPoint(BluePrint(id, vp.blueprint.variables, seq_with_short_wait, vp.blueprint.pumping_points)))
                additional_vp_list.append(ViewPoint(BluePrint(id, vp.blueprint.variables, seq_with_long_wait, pp_for_long_wait)))
            view_points_list += additional_vp_list

            starting_dictionary[id] = ViewPointList(view_points_list)
            starting_dictionary, accepted_alphabet = self.generateViewPointsFromBPMTree(root.childrens[0], starting_dictionary=starting_dictionary, accepted_alphabet=accepted_alphabet)
            starting_dictionary, accepted_alphabet = self.generateViewPointsFromBPMTree(root.childrens[1], starting_dictionary=starting_dictionary, accepted_alphabet=accepted_alphabet)
        else:
            print('Type error' + root.type)
        return starting_dictionary, accepted_alphabet
    
    def generateAdditionalData(self, bpmTree: CTree):
        root = bpmTree.root
        id = root.id
        if root.type == 'task':
            self.types[id] = self.TASK
            #tmp_dict = {}
            #tmp_dict["impact"] = root.impact
            #tmp_dict["probability"] = region_probability
            self.task_dict[id] = root.impact#tmp_dict.copy()
        else:
            id_left_child = root.childrens[0].root.id
            id_right_child = root.childrens[1].root.id
            self.childrens[id] = [id_left_child, id_right_child]
            if root.type == 'sequential':
                self.types[id] = self.SEQUENTIAL
                self.generateAdditionalData(root.childrens[0])
                self.generateAdditionalData(root.childrens[1])
            elif root.type == 'natural':
                self.types[id] = self.NATURAL
                self.nature_dict[id] = [id_left_child, root.probability]
                self.generateAdditionalData(root.childrens[0])
                self.generateAdditionalData(root.childrens[1])
            elif root.type == 'choice':
                self.types[id] = self.CHOICE
                self.generateAdditionalData(root.childrens[0])
                self.generateAdditionalData(root.childrens[1])
            elif root.type == 'parallel':
                self.types[id] = self.PARALLEL
                self.generateAdditionalData(root.childrens[0])
                self.generateAdditionalData(root.childrens[1])
            else:
                print('Type error' + root.type)
        return
    
    def print_vp_list(self) -> None:
        for k in self.VPDict.keys():
            VPListObj = self.VPDict[k]
            for vp in VPListObj.view_point_list:
                print(vp.blueprint)

    def print_active_vp_list(self) -> None:
        for k in self.VPDict.keys():
            VPListObj = self.VPDict[k]
            for idx in VPListObj.ACTIVE_VP_INDICES:
                vp = VPListObj.view_point_list[idx]
                print(vp.blueprint)

    def pre(self):
        self.FAILED = False
        for key in self.VPDict.keys():
            self.VPDict[key].reset()

    def post(self):
        pass

    def copy_VPDict(self):
        VPDict_copy = {}
        for k in self.VPDict.keys():
            VPDict_copy[k] = self.VPDict[k].copy()
        return VPDict_copy

    def step(self, symbol: tuple[int]):
        step_result = self.submit_symbol(symbol)
        if step_result:
            if not any([x != 2 and x != -1 for x in symbol]):
                result = COMPLETE
            else:
                result = CHAR_ACCEPTED

        else:
            result = INVALID_CHAR

        times_accepted = 0
        while result == CHAR_ACCEPTED:
            failed_at_prev_step = self.FAILED
            VPDictCopy = self.copy_VPDict()
            times_accepted += 1
            result = self.step(symbol)
        if times_accepted > 0:
            self.VPDict = VPDictCopy
            self.FAILED = failed_at_prev_step
            return CHAR_ACCEPTED
        return result

    def submit_symbol(self, symbol: tuple[int]):
        if self.FAILED or symbol == None or len(symbol) != self.number_of_nodes: return FAILED
        VPListObj = self.VPGeneral
        VP_indices_to_remove = []
        char = symbol[0]
        for idx in VPListObj.ACTIVE_VP_INDICES:
            failed = False
            vp = VPListObj.view_point_list[idx]
            pp = vp.blueprint.pumping_points
            var = vp.blueprint.variables
            seq = vp.blueprint.sequences
            if vp.index not in pp:
                step_done = vp.step()
                if step_done:
                    if [symbol[v] for v in var] != [s[vp.index] for s in seq]:
                        failed = True
                else:
                    failed = True
            else:
                if [symbol[v] for v in var] != [s[vp.index] for s in seq]:
                    failed = True
                if failed:
                    failed = False
                    step_done = vp.step()
                    if step_done:
                        if [symbol[v] for v in var] != [s[vp.index] for s in seq]:
                            failed = True
                    else:
                        failed = True
            if failed:
                VPListObj.ACTIVE_VP -= 1
                VP_indices_to_remove.append(idx)
                if VPListObj.ACTIVE_VP == 0:
                    self.FAILED = True
                    return FAILED
        for _idx in VP_indices_to_remove: VPListObj.ACTIVE_VP_INDICES.remove(_idx)
        result = self.submit_symbol_rec(symbol, status=char)
        return result

    def submit_symbol_rec(self, symbol: tuple[int], ids_vp_to_check: list[int] = [0], status = 1):
        if self.FAILED: return FAILED
        for id in ids_vp_to_check:
            VP_indices_to_remove = []
            VPListObj = self.VPDict[id]
            char = symbol[id]
            if (status == -1 or status == 0) and char != status:
                self.FAILED = True
                return FAILED
            for idx in VPListObj.ACTIVE_VP_INDICES:
                failed = False
                vp = VPListObj.view_point_list[idx]
                pp = vp.blueprint.pumping_points
                var = vp.blueprint.variables
                seq = vp.blueprint.sequences
                if char == 2:
                    if self.types[id] != self.TASK:
                        if self.types[id] == self.CHOICE or self.types[id] == self.NATURAL:
                            if [symbol[v] for v in var] != [2,-1] and [symbol[v] for v in var] != [-1,2]:
                                self.FAILED = True
                                return FAILED
                        else:
                            if [symbol[v] for v in var] != [2,2]:
                                self.FAILED = True
                                return FAILED
                if ([symbol[v] for v in var] == [2,-1] or [symbol[v] for v in var] == [-1,2] or [symbol[v] for v in var] == [2,2]) and char != 2:
                    self.FAILED = True
                    return FAILED
                if vp.index not in pp:
                    step_done = vp.step()
                    if step_done:
                        if [symbol[v] for v in var] != [s[vp.index] for s in seq]:
                            failed = True
                        if (failed or self.types[id] == self.CHOICE) and char == 0 and self.types[id] != self.TASK:
                            vp.step_back()
                            failed = False
                    else:
                        failed = True
                else:
                    if [symbol[v] for v in var] != [s[vp.index] for s in seq]:
                        failed = True
                    if failed:
                        failed = False
                        step_done = vp.step()
                        if step_done:
                            if [symbol[v] for v in var] != [s[vp.index] for s in seq]:
                                failed = True
                        else:
                            failed = True
                if failed:
                    VPListObj.ACTIVE_VP -= 1
                    VP_indices_to_remove.append(idx)
                    if VPListObj.ACTIVE_VP == 0:
                        self.FAILED = True
                        return FAILED
            for _idx in VP_indices_to_remove: VPListObj.ACTIVE_VP_INDICES.remove(_idx)
            if len(var) > 1:
                ret = self.submit_symbol_rec(symbol, var, char)
                if ret == FAILED: return FAILED
        return ADMITTED