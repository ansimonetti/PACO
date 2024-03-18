import numpy as np

def sum(list1, list2):
    if len(list1) != len(list2):
        if len(list1) == 0:
            return list2
        if len(list2) == 0:
            return list1
        return None
    else:
        return [x[0] + x[1] for x in zip(list1, list2)]
    
def product(list, n):
    if len(list) == 0: return []
    return [x*n for x in list]

def equals(list1, list2):
    if len(list1) != len(list2): return False
    return all([x[0] == x[1] for x in zip(list1, list2)])

def ge(list1, list2):
    if len(list1) != len(list2): return False
    return all([x[0] >= x[1] for x in zip(list1, list2)])

def g(list1, list2):
    if len(list1) != len(list2): return False
    return all([x[0] > x[1] for x in zip(list1, list2)])

def le(list1, list2):
    if len(list1) != len(list2): return False
    return all([x[0] <= x[1] for x in zip(list1, list2)])

def l(list1, list2):
    if len(list1) != len(list2): return False
    return all([x[0] < x[1] for x in zip(list1, list2)])

def euclidean_distance(list1, list2):
    if len(list1) != len(list2): return None
    return np.sqrt(np.sum(np.square(np.array(list1) - np.array(list2))))