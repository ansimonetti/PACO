import unittest
import numpy as np

from src.paco.searcher.found_strategy import compare_bound


class TestFoundStrategy(unittest.TestCase):
	def test_compare_bound(self):
		#Doesn't work with 1e-15
		cei = np.array([133.4, 7], dtype=np.float64)
		bound = np.array([135, 7.0], dtype=np.float64)
		expected_output = np.array([0, 0])
		output = compare_bound(cei, bound)
		np.testing.assert_array_equal(output, expected_output)

		# Test case 1: Exact equality
		cei = np.array([1.0, -1.0, 0.0])
		bound = np.array([1.0, -1.0, 0.0])
		expected_output = np.array([0, 0, 0])
		output = compare_bound(cei, bound)
		np.testing.assert_array_equal(output, expected_output)

		# Test case 2: cei less than bound
		cei = np.array([0.99999999999999, -1.00000000000001, -1e-15])
		bound = np.array([1.0, -1.0, 0.0])
		expected_output = np.array([0, 0, 0])
		output = compare_bound(cei, bound)
		np.testing.assert_array_equal(output, expected_output)

		# Test case 3: cei greater than bound
		cei = np.array([1.00000000000001, -0.99999999999999, 1e-14])
		bound = np.array([1.0, -1.0, 0.0])
		expected_output = np.array([1, 1, 1])
		output = compare_bound(cei, bound)
		np.testing.assert_array_equal(output, expected_output)

		# Test case 4: Mixed values
		cei = np.array([1.0, 2.0, 3.0, 4.0])
		bound = np.array([1.0, 2.0, 2.999999999999, 5.0])
		expected_output = np.array([0, 0, 1, 0])
		output = compare_bound(cei, bound)
		np.testing.assert_array_equal(output, expected_output)

		# Test case 5: Negative numbers and zeros
		cei = np.array([-5.0, 0.0, 5.0])
		bound = np.array([-5.0, 0.0, 5.0])
		expected_output = np.array([0, 0, 0])
		output = compare_bound(cei, bound)
		np.testing.assert_array_equal(output, expected_output)


if __name__ == '__main__':
	unittest.main()
