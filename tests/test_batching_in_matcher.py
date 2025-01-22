import os
import sys
import unittest

sys.path.append("../src")
from unittest import TestCase, mock
from harmony.matching.matcher import process_items_in_batches


# Mock LLM function
def mock_llm_function(batch):
    """Simulates processing a batch."""
    return [f"Processed: {item}" for item in batch]


class TestMatcherBatching(TestCase):

    @mock.patch.dict(os.environ, {"BATCH_SIZE": "5"})
    def test_batched_processing(self):
        """Test that 10 items are divided into 2 batches of 5 each."""
        items = [f"item{i}" for i in range(10)]  # 10 items to process
        results = process_items_in_batches(items, mock_llm_function)

        self.assertEqual(len(results), 10)

        expected = [
            "Processed: item0", "Processed: item1", "Processed: item2", "Processed: item3", "Processed: item4",
            "Processed: item5", "Processed: item6", "Processed: item7", "Processed: item8", "Processed: item9",
        ]
        self.assertEqual(results, expected)

    @mock.patch.dict(os.environ, {"BATCH_SIZE": "5"})
    def test_large_batch_size(self):
        """Test batch size greater than input size."""
        items = [f"item{i}" for i in range(3)]  # Only 3 items
        results = process_items_in_batches(items, mock_llm_function)

        self.assertEqual(len(results), 3)

        expected = [
            "Processed: item0", "Processed: item1", "Processed: item2",
        ]
        self.assertEqual(results, expected)

    @mock.patch.dict(os.environ, {"BATCH_SIZE": "0"})
    def test_no_batching(self):
        """Test no batching (all items processed in one batch)."""
        items = [f"item{i}" for i in range(10)]  # 10 items to process
        results = process_items_in_batches(items, mock_llm_function)

        self.assertEqual(len(results), 10)

        expected = [
            "Processed: item0", "Processed: item1", "Processed: item2", "Processed: item3", "Processed: item4",
            "Processed: item5", "Processed: item6", "Processed: item7", "Processed: item8", "Processed: item9",
        ]
        self.assertEqual(results, expected)

    @mock.patch.dict(os.environ, {"BATCH_SIZE": "-5"})
    def test_negative_batch_size(self):
        """Test when BATCH_SIZE is negative, it defaults to 0."""
        items = [f"item{i}" for i in range(10)]
        results = process_items_in_batches(items, mock_llm_function)
        self.assertEqual(len(results), 10)

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_default_batch_size(self):
        """Test when BATCH_SIZE is not set, it defaults to 1000."""
        items = [f"item{i}" for i in range(10)]
        results = process_items_in_batches(items, mock_llm_function)
        self.assertEqual(len(results), 10)

    @mock.patch.dict(os.environ, {"BATCH_SIZE": "invalid"})
    def test_invalid_batch_size(self):
        """Test when BATCH_SIZE is invalid, it defaults to 1000."""
        items = [f"item{i}" for i in range(10)]
        results = process_items_in_batches(items, mock_llm_function)
        self.assertEqual(len(results), 10)


if __name__ == "__main__":
    unittest.main()
