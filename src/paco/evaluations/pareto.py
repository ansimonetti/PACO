import numpy as np

def get_dominated_vectors(A, B):
	# Find vectors in A dominated by any vector in B
	dominated_A = []
	for a in A:
		dominated = False
		for b in B:
			if np.all(b >= a) and np.any(b > a):
				dominated = True
				break
		if dominated:
			dominated_A.append(a)

	# Find vectors in B dominated by any vector in A
	dominated_B = []
	for b in B:
		dominated = False
		for a in A:
			if np.all(a >= b) and np.any(a > b):
				dominated = True
				break
		if dominated:
			dominated_B.append(b)

	return dominated_A, dominated_B



def get_max_dominating_vectors(frontier):
	max_dominating_vectors = []

	for i, arr in enumerate(frontier):
		is_dominating = True
		for j, other_arr in enumerate(frontier):
			if i != j and (np.all(other_arr >= arr) and np.any(other_arr > arr)):
				is_dominating = False
				break
		if is_dominating:
			if not any(np.array_equal(arr, x) for x in max_dominating_vectors):
				max_dominating_vectors.append(arr)

	return max_dominating_vectors


def get_min_dominated_impacts(frontier):
	minimally_dominated_impacts = []
	for i, arr in enumerate(frontier):
		dominated = False
		for j, other_arr in enumerate(frontier):
			if (i != j and # arr is strictly dominated by other_arr
					np.all(other_arr <= arr) and np.any(other_arr < arr)):
				dominated = True
				break
		if not dominated:
			# Check for duplicates
			if not any(np.array_equal(arr, x) for x in minimally_dominated_impacts):
				minimally_dominated_impacts.append(arr)

	return minimally_dominated_impacts
