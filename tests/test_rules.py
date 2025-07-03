# TurkishCheckers/tests/test_rules.py
import unittest
import sys
import os

# --- Proje Kök Dizinini Python Yoluna Ekle ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# ---------------------------------------------

from core import rules, board as board_utils

class TestGameRules(unittest.TestCase):
    """
    Oyunun temel kurallarını (core/rules.py) test etmek için birim testleri.
    """

    def test_get_opponent(self):
        self.assertEqual(rules.get_opponent('W'), 'B')
        self.assertEqual(rules.get_opponent('B'), 'W')

    def test_normal_move_generation(self):
        """
        Normal taşlar için başlangıçtaki ileri hamleleri test eder.
        """
        board = board_utils.setup_new_board()
        white_moves = rules.get_all_possible_moves('W', board)
        self.assertEqual(white_moves['type'], 'normal')
        # Başlangıçta sadece 5. sıradaki 8 taş ileri hareket edebilir.
        self.assertEqual(len(white_moves['moves']), 8, "Başlangıçta sadece 8 ileri hamle olmalı.")

    def test_single_capture_is_mandatory(self):
        board = board_utils.setup_new_board()
        board[4][0] = 'B'
        white_moves = rules.get_all_possible_moves('W', board)
        self.assertEqual(white_moves['type'], 'capture')
        self.assertEqual(len(white_moves['moves']), 1)
        self.assertEqual(white_moves['moves'][0], [(5, 0), (3, 0)])

    def test_longest_capture_is_mandatory(self):
        """Dikeyde en uzun taş alma yolunun zorunlu olmasını test eder."""
        board = [([board_utils.EMPTY_SQUARE] * 8) for _ in range(8)]
        board[7][2] = 'W'
        board[6][2] = 'B'
        board[4][2] = 'B'
        
        white_moves = rules.get_all_possible_moves('W', board)
        self.assertEqual(white_moves['type'], 'capture', "Taş alma hamlesi bulunmalıydı.")
        self.assertEqual(len(white_moves['moves']), 1, "Sadece bir adet en uzun yol olmalı.")
        self.assertEqual(white_moves['moves'][0], [(7, 2), (5, 2), (3, 2)], "En uzun yol doğru hesaplanmadı.")

    def test_dama_movement(self):
        """
        Dama hareket sayısını doğru beklentiyle test eder.
        """
        board = [([board_utils.EMPTY_SQUARE] * 8) for _ in range(8)]
        board[3][3] = 'w'
        moves = rules.get_all_possible_moves('W', board)
        self.assertEqual(moves['type'], 'normal')
        # Merkezdeki (3,3) bir dama boş tahtada 3(yukarı)+4(aşağı)+3(sol)+4(sağ) = 14 kareye gidebilir.
        self.assertEqual(len(moves['moves']), 14, "Merkezdeki damanın 14 hamlesi olmalı.")

    def test_dama_long_capture(self):
        """Damanın uzaktaki bir taşı almasını test eder."""
        board = [([board_utils.EMPTY_SQUARE] * 8) for _ in range(8)]
        board[7][4] = 'w'
        board[3][4] = 'b'
        
        moves = rules.get_all_possible_moves('W', board)
        self.assertEqual(moves['type'], 'capture')
        self.assertEqual(len(moves['moves']), 3)
        self.assertIn([(7, 4), (2, 4)], moves['moves'])

    def test_player_is_blocked(self):
        """
        DÜZELTİLDİ (v2): Bir oyuncunun hamlesi kalmadığında bloke olmasını test eder.
        """
        board = [([board_utils.EMPTY_SQUARE] * 8) for _ in range(8)]
        board[0][0] = 'B'
        board[1][0] = 'W' # İleri gitmeyi engeller
        board[0][1] = 'W' # Yana gitmeyi engeller
        board[2][0] = 'W' # İleri zıplamayı engeller
        board[0][2] = 'W' # Yana zıplamayı engeller
        
        is_blocked = rules.is_player_blocked('B', board)
        self.assertTrue(is_blocked, "Oyuncunun tüm hamleleri engellendiği için bloke edilmiş sayılmalı.")

    def test_promotion(self):
        board = [([board_utils.EMPTY_SQUARE] * 8) for _ in range(8)]
        board[1][0] = 'W'
        rules.apply_normal_move_on_board((1, 0), (0, 0), board)
        self.assertEqual(board[0][0], 'w')

if __name__ == '__main__':
    unittest.main()
