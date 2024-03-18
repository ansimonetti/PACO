from automaton_graph import AutomatonGraph, ANode, AGraph
import array_operations

class GameSolver:
    def __init__(self, automaton_graph: AutomatonGraph, goal) -> None:
        self.automaton_graph = automaton_graph
        self.goal = goal
        final_states = self.automaton_graph.final_states
        impacts = self.automaton_graph.impacts
        if len(final_states) == 0:
            self.final_states_sorted = []
        else:
            final_states_impacts = list(zip(final_states, impacts))
            self.final_states_sorted = sorted(final_states_impacts, key=lambda x : array_operations.euclidean_distance(x[1], self.goal), reverse=False)

    def compute_winning_final_set(self, i = 0, current_set = []):
        if i >= len(self.final_states_sorted):
            if self.attractor_solver([x[0] for x in current_set]):
                return current_set
            else:
                return None
        else:             
            impact = []
            for x in current_set:
                impact = array_operations.sum(impact, x[1])
            r = None
            if array_operations.le(array_operations.sum(impact, self.final_states_sorted[i][1]), self.goal):
                current_set_augmented = current_set.copy()
                current_set_augmented.append(self.final_states_sorted[i])
                r = self.compute_winning_final_set(i+1, current_set_augmented)
            
            if r == None:
                return self.compute_winning_final_set(i+1, current_set)
            else:
                return r


    
    # def general_solver(self):
    #     index1 = 0
    #     while index1 < len(final_states_impacts_sorted):
    #         index2 = index1 + 1
    #         not_used_indexes = list(range(index2, len(final_states_impacts_sorted), 1))
    #         while True:
    #             total_expected_impact = final_states_impacts_sorted[index1][1]
    #             if array_operations.le(total_expected_impact, self.goal):
    #                 starting_set = [final_states_impacts_sorted[index1][0]]
    #             else: 
    #                 break
    #             used_indexes = []
    #             for i in not_used_indexes:
    #                 if array_operations.le(array_operations.sum(total_expected_impact, final_states_impacts_sorted[i][1]), self.goal):
    #                     total_expected_impact = array_operations.sum(total_expected_impact, final_states_impacts_sorted[i][1])
    #                     starting_set.append(str(final_states_impacts_sorted[i][0]))
    #                     used_indexes.append(i)
    #                 else:
    #                     if len(starting_set) == 1: used_indexes.append(i)
    #             for i in used_indexes: not_used_indexes.remove(i)
    #             success = self.instance_solver(starting_set)
    #             if success: return True                    
    #             if len(not_used_indexes) == 0: break
    #         index1 += 1
    #     return False        

    def attractor_solver(self, starting_set):
        set_after_interaction = starting_set
        starting_set = []
        while set_after_interaction != starting_set:
            starting_set = set_after_interaction
            set_after_interaction = self.attractor_solver_rec(self.automaton_graph.processed_graph.init_node, starting_set.copy())
        if self.automaton_graph.processed_graph.init_node.state_id in set_after_interaction:
            return True
        else:
            return False
        
    def attractor_solver_rec(self, node: ANode, increasing_set):
        if node.is_final_state:
            return increasing_set
        else:
            next_states = [node.transitions[k].init_node.state_id for k in node.transitions.keys() if node.transitions[k].init_node.state_id != node.state_id]
            if node.is_square_node:
                if all([s in increasing_set for s in next_states]):
                    if node.state_id not in increasing_set:
                        increasing_set.append(node.state_id)
            else:
                if any([s in increasing_set for s in next_states]):
                    if node.state_id not in increasing_set:
                        increasing_set.append(node.state_id)
            for k in node.transitions.keys():
                if node.transitions[k].init_node.state_id != node.state_id:
                    increasing_set = self.attractor_solver_rec(node.transitions[k].init_node, increasing_set)
            return increasing_set
