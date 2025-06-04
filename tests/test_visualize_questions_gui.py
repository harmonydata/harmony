import unittest
from unittest.mock import patch, MagicMock
from harmony.matching.visualize_questions_gui import (
    draw_cosine_similarity_matrix,
    draw_clusters_scatter_plot,
    draw_network_graph,
    visualize_questions
)


class TestHarmonyBasic(unittest.TestCase):
    def setUp(self):
        # mock the embedding function to return dummy data
        self.patcher = patch(
            'harmony.matching.default_matcher.convert_texts_to_vector',
            return_value=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
        )
        self.mock_convert = self.patcher.start()

        # simple mock objects for the Axes and Canvas objects
        self.mock_ax = MagicMock()
        self.mock_canvas = MagicMock()

    def tearDown(self):
        self.patcher.stop()

    def test_draw_cosine_similarity_matrix(self):
        """Check if the draw_cosine_similarity_matrix function runs without error"""
        draw_cosine_similarity_matrix(["Q1", "Q2", "Q3", "Q4", "Q5"], self.mock_ax, self.mock_canvas)
        self.assertTrue(True)

    def test_draw_clusters_scatter_plot(self):
        """Just check if the draw_clusters_scatter_plot function runs without error"""
        draw_clusters_scatter_plot(["Q1", "Q2", "Q3", "Q4", "Q5"], self.mock_ax, self.mock_canvas)
        self.assertTrue(True)

    def test_draw_network_graph(self):
        """Just check if the draw_network_graph function runs without error"""
        draw_network_graph(["Q1", "Q2", "Q3", "Q4", "Q5"], self.mock_ax, self.mock_canvas)
        self.assertTrue(True)

    def test_empty_questions(self):
        """Check empty input exits correctly"""
        with self.assertRaises(SystemExit) as se:
            visualize_questions([])
        self.assertEqual(se.exception.code, 1)

if __name__ == '__main__':
    unittest.main()