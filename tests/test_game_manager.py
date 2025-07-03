# TurkishCheckers/tests/test_game_manager.py
import unittest
import sys
import os

# --- Proje Kök Dizinini Python Yoluna Ekle ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# ---------------------------------------------

from game.game_manager import GameManager

class TestGameManager(unittest.TestCase):
    """
    Oyunun durumunu ve akışını yöneten GameManager sınıfını test eder.
    """

    def setUp(self):
        """Her testten önce yeni bir oyun yöneticisi nesnesi oluşturur."""
        self.game = GameManager()
        self.game.setup_new_game()

    def test_initial_board_setup(self):
        """Oyunun başlangıç durumunu kontrol eder."""
        self.assertEqual(self.game.board[1][0], 'B')
        self.assertEqual(self.game.board[5][0], 'W')
        self.assertEqual(self.game.current_player, 'W')
        self.assertFalse(self.game.game_over)

    def test_valid_normal_move(self):
        """Geçerli bir normal hamlenin yapılmasını test eder."""
        result = self.game.play_turn((5, 0), (4, 0))
        self.assertTrue(result['success'])
        self.assertEqual(self.game.board[5][0], ' ')
        self.assertEqual(self.game.board[4][0], 'W')
        self.assertEqual(self.game.current_player, 'B')

    def test_invalid_move_against_rules(self):
        """Kurallara aykırı bir hamlenin (örn: geri gitme) reddedilmesini test eder."""
        self.game.play_turn((5, 0), (4, 0))
        self.game.play_turn((2, 0), (3, 0))
        
        result = self.game.play_turn((4, 0), (5, 0))
        self.assertFalse(result['success'])
        self.assertEqual(self.game.board[4][0], 'W')
        self.assertEqual(self.game.current_player, 'W')

    def test_single_capture_and_player_switch(self):
        """Tekli taş alımını ve sonrasında sıranın değişmesini test eder."""
        self.game.board[4][0] = 'B'
        result = self.game.play_turn((5, 0), (3, 0))
        
        self.assertTrue(result['success'])
        self.assertEqual(self.game.board[4][0], ' ')
        self.assertEqual(self.game.board[3][0], 'W')
        self.assertEqual(self.game.current_player, 'B')

    def test_mandatory_capture_blocks_normal_move(self):
        """Zorunlu taş alma varken normal bir hamlenin engellenmesini test eder."""
        self.game.board[4][0] = 'B'
        
        result = self.game.play_turn((5, 1), (4, 1))
        
        self.assertFalse(result['success'])
        self.assertIn("Zorunlu taş alma", result['message'])
        self.assertEqual(self.game.current_player, 'W')

    def test_multi_capture_turn_does_not_change_midway(self):
        """Çoklu taş alımı sırasında sıranın değişmemesini test eder."""
        self.game.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.game.board[5][2] = 'W'
        self.game.board[4][2] = 'B'
        self.game.board[2][2] = 'B'
        self.game.current_player = 'W'
        
        result = self.game.play_turn((5, 2), (3, 2))
        
        self.assertTrue(result['success'])
        self.assertEqual(self.game.current_player, 'W', "Çoklu alım sonrası sıra değişmemeli.")
        self.assertIn("Tekrar oynamalısınız!", self.game.message)
        
        result2 = self.game.play_turn((3, 2), (1, 2))
        self.assertTrue(result2['success'])
        self.assertEqual(self.game.current_player, 'B', "Tüm alımlar bitince sıra değişmeli.")

    def test_game_over_when_no_pieces_left(self):
        """Bir oyuncunun tüm taşları bittiğinde oyunun bitmesini test eder."""
        self.game.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.game.board[5][0] = 'W'
        self.game.board[4][0] = 'B'
        self.game.current_player = 'W'
        
        self.game.play_turn((5, 0), (3, 0))
        
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, 'W')
        self.assertIn("Tüm taşlar alındı", self.game.message)

    def test_game_over_when_player_is_blocked(self):
        """
        DÜZELTİLDİ (v2): Bir oyuncunun hamlesi kalmadığında oyunun bitmesini test eder.
        """
        self.game.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.game.board[0][0] = 'B'
        self.game.board[1][0] = 'W' # Siyahın ileri gitmesini engeller
        self.game.board[0][1] = 'W' # Siyahın yana gitmesini engeller
        self.game.board[2][0] = 'W' # Siyahın ileri zıplamasını da engeller
        self.game.board[0][2] = 'W' # Siyahın yana zıplamasını da engeller
        self.game.board[7][7] = 'W' # Oyun bitmesin diye ek beyaz taş
        
        self.game.current_player = 'B'
        self.game.check_game_over() # Manuel olarak kontrolü tetikle
        
        self.assertTrue(self.game.game_over, "Siyah'ın hamlesi olmadığı için oyun bitmeli.")
        self.assertEqual(self.game.winner, 'W', "Kazanan Beyaz olmalı.")
        self.assertIn("bloke oldu", self.game.message)

    def test_draw_by_move_rule(self):
        """40 hamle kuralı (taş alınmadan) ile oyunun berabere bitmesini test eder."""
        self.game.moves_since_last_capture = 39
        
        self.game.play_turn((5,0), (4,0))

        self.assertTrue(self.game.game_over)
        self.assertIsNone(self.game.winner)
        self.assertIn("Berabere", self.game.message)

if __name__ == '__main__':
    unittest.main()
