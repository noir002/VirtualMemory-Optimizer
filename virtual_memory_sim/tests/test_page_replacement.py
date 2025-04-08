import unittest
from src.algorithms.page_replacement import LRUAlgorithm, OptimalAlgorithm

class TestPageReplacement(unittest.TestCase):
    def setUp(self):
        # Set up test environment with 3 page frames
        self.total_frames = 3
        self.lru = LRUAlgorithm(self.total_frames)
        self.optimal = OptimalAlgorithm(self.total_frames)
        
    def test_lru_algorithm(self):
        # Test LRU with a typical reference string
        sequence = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
        page_faults, final_memory, history = self.lru.simulate(sequence)
        
        # Assert that page faults occurred
        self.assertGreater(page_faults, 0)
        # Memory should have exactly 'total_frames' pages at the end
        self.assertEqual(len(final_memory), self.total_frames)
        # History should record an entry for every page access
        self.assertEqual(len(history), len(sequence))
        
    def test_optimal_algorithm(self):
        # Test Optimal algorithm with the same sequence
        sequence = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
        page_faults, final_memory, history = self.optimal.simulate(sequence)
        
        # Assert that page faults occurred
        self.assertGreater(page_faults, 0)
        # Memory should have exactly 'total_frames' pages at the end
        self.assertEqual(len(final_memory), self.total_frames)
        # History should record an entry for every page access
        self.assertEqual(len(history), len(sequence))
        
    def test_empty_frames(self):
        # Test with a short sequence where all pages fit into memory
        sequence = [1, 2]
        
        # Test LRU behavior
        page_faults, final_memory, _ = self.lru.simulate(sequence)
        self.assertEqual(page_faults, 2)  # Each unique page causes a fault
        self.assertEqual(final_memory.count(-1), 1)  # One empty slot remains
        
        # Test Optimal behavior
        page_faults, final_memory, _ = self.optimal.simulate(sequence)
        self.assertEqual(page_faults, 2)
        self.assertEqual(final_memory.count(-1), 1)

# Run the tests
if __name__ == '__main__':
    unittest.main()
