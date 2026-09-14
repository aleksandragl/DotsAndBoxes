import unittest
from dots_and_boxes import (
    apply_move,
    get_completed_boxes,
    get_available_moves,
    evaluate_state,
    minimax,
    computer_move_minimax,
    computer_move_greedy,
    measure_performance,
    BOXES,
    INITIAL_STATE,
)


class TestDotsAndBoxes(unittest.TestCase):

    def test_initial_state(self):
        state = INITIAL_STATE
        available = get_available_moves(state.split(".")[0])
        self.assertEqual(len(available), 7)
        self.assertEqual(get_completed_boxes(state.split(".")[0]), [])

    def test_apply_move_normal_turn_switch(self):
        new_state = apply_move("0000000.A", 0)
        self.assertEqual(new_state, "1000000.B")
        next_state = apply_move(new_state, 1)
        self.assertEqual(next_state, "1100000.A")

    def test_apply_move_complete_box_gives_extra_turn(self):
        # Kast 0 (0, 2, 3, 5): 0, 2, 3 on tõmmatud
        state = "1011000.A"
        new_state = apply_move(state, 5)
        self.assertEqual(new_state, "1011010.A")
        completed = get_completed_boxes(new_state.split(".")[0])
        self.assertEqual(completed, [0])

    def test_apply_move_double_box_completion(self):
        state = "1110111.B"
        new_state = apply_move(state, 3)
        self.assertEqual(new_state, "1111111.B")
        completed = get_completed_boxes(new_state.split(".")[0])
        self.assertEqual(completed, [0, 1])

    def test_apply_move_invalid_move(self):
        state = "1000000.A"
        with self.assertRaises(ValueError):
            apply_move(state, 0)
        with self.assertRaises(ValueError):
            apply_move(state, 7)

    def test_evaluate_state(self):
        # Algseis: 0 joont igal kastil -> 0.0
        self.assertEqual(evaluate_state("0000000.A"), 0.0)

        # 1 joon Kastil 0 (joon 0) -> +0.5
        self.assertEqual(evaluate_state("1000000.A"), 0.5)

        # 2 joont Kastil 0 (jooned 0 ja 2) -> +2.0
        self.assertEqual(evaluate_state("1010000.A"), 2.0)

        # 3 joont Kastil 0 (0, 2, 5) -> +5.0
        self.assertEqual(evaluate_state("1010010.A"), 5.0)

        # Ühine joon 3 (Kast 0 ja Kast 1 saavad mõlemad 1 joone): 0.5 + 0.5 = 1.0
        self.assertEqual(evaluate_state("0001000.A"), 1.0)

        # Kast 0 omab 3 joont (0, 2, 3) = 5.0, Kast 1 omab joont 3 = 0.5 -> kokku 5.5
        self.assertEqual(evaluate_state("1011000.A"), 5.5)

    def test_minimax_takes_immediate_box(self):
        # Seis: 1011000.B (Kast 0 vajab joont 5)
        state = "1011000.B"
        best_move = computer_move_minimax(state, depth=4)
        self.assertEqual(best_move, 5)

    def test_greedy_takes_immediate_box(self):
        # Seis: 1011000.B (Kast 0 vajab joont 5)
        state = "1011000.B"
        move = computer_move_greedy(state)
        self.assertEqual(move, 5)

    def test_greedy_avoids_giving_3rd_line(self):
        # Kui joon 0 ja 2 on tõmmatud (Kastil 0 on 2 joont).
        # Kui tõmmatakse joon 5 või 3, saab sellest 3. joon (halb).
        # Greedy peaks eelistama ohutut joont teisest kastist (nt joon 4)
        state = "1010000.B"
        move = computer_move_greedy(state)
        new_lines = apply_move(state, move).split(".")[0]
        # Kontrollime, et käik ei tekitanud kolmandat joont, kui oli võimalik vältida
        creates_3 = any(sum(1 for idx in box if new_lines[idx] == "1") == 3 for box in BOXES)
        self.assertFalse(creates_3)

    def test_measure_performance(self):
        results = measure_performance(INITIAL_STATE)
        self.assertEqual(len(results), 6)
        for r in results:
            self.assertIn("depth", r)
            self.assertIn("nodes", r)
            self.assertIn("time", r)
            self.assertIn("nodes_per_min", r)
            self.assertGreater(r["nodes"], 0)
            self.assertGreaterEqual(r["time"], 0.0)
            self.assertGreaterEqual(r["nodes_per_min"], 0.0)


if __name__ == "__main__":
    unittest.main()
