import unittest
import numpy as np
from harmony.matching.matcher import batch_process, vectorize_items_with_batching

class TestBatchProcessing(unittest.TestCase):

    def setUp(self):
        self.vectorization_function = lambda texts: np.array([[len(text)] for text in texts])

    def test_batch_process(self):
        items = ["item1", "item2", "item3", "item4", "item5"]
        batch_size = 2
        batches = batch_process(items, batch_size)  
        expected_batches = [["item1", "item2"], ["item3", "item4"], ["item5"]]
        self.assertEqual(batches, expected_batches)

    def test_vectorize_items_with_batching(self):
        items = ["short", "medium length", "a bit longer", "longest item in the list"]
        batch_size = 2
        vectors = vectorize_items_with_batching(items, self.vectorization_function, batch_size)
        expected_vectors = np.array([[5], [13], [12], [24]]) 
        np.testing.assert_array_equal(vectors, expected_vectors)

    def test_edge_case_single_item(self):
        items = ["single item"]
        batch_size = 2
        vectors = vectorize_items_with_batching(items, self.vectorization_function, batch_size)
        expected_vectors = np.array([[11]]) 
        np.testing.assert_array_equal(vectors, expected_vectors)

    def test_edge_case_empty_list(self):
        items = []
        batch_size = 2
        vectors = vectorize_items_with_batching(items, self.vectorization_function, batch_size)
        expected_vectors = np.array([])  
        np.testing.assert_array_equal(vectors, expected_vectors)

    def test_large_batch_size(self):
        items = ["item1", "item2", "item3"]
        batch_size = 10  
        batches = batch_process(items, batch_size) 
        expected_batches = [["item1", "item2", "item3"]]
        self.assertEqual(batches, expected_batches)

if __name__ == "__main__":
    unittest.main()
