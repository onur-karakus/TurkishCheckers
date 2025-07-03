# test_game_logic.py
import unittest
import sys
import os

# Proje kök dizinini Python yoluna ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game_logic import Game

class TestGameLogic(unittest.TestCase):
    """
    Oyunun temel mantığını test etmek için birim testleri.
    NİHAİ REVİZYON: Tüm test senaryoları, mantık hatalarını kesin olarak
    yakalayacak ve kararlı çalışacak şekilde güncellendi.
    """

    def setUp(self):
        """Her testten önce yeni bir oyun nesnesi oluşturur."""
        self.game = Game()
        self.game.setup_new_game()

    def _apply_move(self, start, end):
        """Yardımcı fonksiyon: Hamleyi doğrular ve uygular."""
        result = self.game.play_turn(start, end)
        if result['success']:
            self.game.apply_move_from_path(result['path'], result['type'])
        return result

    def test_initial_board_setup(self):
        self.assertEqual(self.game.board[1][0], 'B')
        self.assertEqual(self.game.board[5][0], 'W')
        self.assertEqual(self.game.current_player, 'W')

    def test_normal_move_forward(self):
        self._apply_move((5, 0), (4, 0))
        self.assertEqual(self.game.board[5][0], ' ')
        self.assertEqual(self.game.board[4][0], 'W')
        self.assertEqual(self.game.current_player, 'B')

    def test_invalid_move_backward(self):
        self._apply_move((5, 0), (4, 0)) # W
        self._apply_move((2, 0), (3, 0)) # B
        result = self._apply_move((4, 0), (5, 0)) # W (geri)
        self.assertFalse(result['success'])
        self.assertEqual(self.game.current_player, 'W')

    def test_single_capture(self):
        self.game.board[4][0] = 'B'
        self._apply_move((5, 0), (3, 0))
        self.assertEqual(self.game.board[4][0], ' ')
        self.assertEqual(self.game.board[3][0], 'W')
        self.assertEqual(self.game.current_player, 'B')

    def test_mandatory_capture(self):
        self.game.board[4][0] = 'B'
        result = self._apply_move((5, 1), (4, 1))
        self.assertFalse(result['success'])
        self.assertIn("Zorunlu taş alma", result['message'])

    def test_promotion_to_dama(self):
        self.game.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.game.board[1][0] = 'W'
        self.game.board[7][7] = 'B' # Oyun bitmesin diye
        self._apply_move((1, 0), (0, 0))
        self.assertEqual(self.game.board[0][0], 'w')
        self.assertEqual(self.game.current_player, 'B')

    def test_dama_movement(self):
        self.game.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.game.board[4][4] = 'w'
        self.game.board[0][0] = 'B' # Oyun bitmesin diye
        self.game.current_player = 'W'
        self._apply_move((4, 4), (1, 4))
        self.assertEqual(self.game.board[1][4], 'w')
        self.assertEqual(self.game.current_player, 'B')

    def test_dama_capture(self):
        self.game.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.game.board[4][4] = 'w'
        self.game.board[2][4] = 'B'
        self.game.board[0][0] = 'B' # Oyun bitmesin diye
        self.game.current_player = 'W'
        self._apply_move((4, 4), (1, 4))
        self.assertEqual(self.game.board[2][4], ' ')
        self.assertEqual(self.game.board[1][4], 'w')
        self.assertEqual(self.game.current_player, 'B')

    def test_game_over_no_pieces(self):
        self.game.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.game.board[5][0] = 'W'
        self.game.board[4][0] = 'B'
        self.game.current_player = 'W'
        self._apply_move((5, 0), (3, 0))
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, 'W')

    def test_multi_capture_turn_does_not_change(self):
        self.game.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.game.board[5][2] = 'W'
        self.game.board[4][2] = 'B'
        self.game.board[2][2] = 'B'
        self.game.current_player = 'W'
        
        self._apply_move((5, 2), (3, 2))
        self.assertEqual(self.game.current_player, 'W', "Çoklu alım sonrası sıra değişmemeli.")
        self.assertIn("Tekrar oynamalısınız!", self.game.message)
        
        self._apply_move((3, 2), (1, 2))
        self.assertEqual(self.game.current_player, 'B', "Tüm alımlar bitince sıra değişmeli.")

    def test_dama_multi_capture(self):
        self.game.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.game.board[7][4] = 'w'
        self.game.board[5][4] = 'B'
        self.game.board[2][4] = 'B'
        self.game.board[0][7] = 'B' # Oyun bitmesin diye
        self.game.current_player = 'W'
        
        result = self._apply_move((7, 4), (1, 4))
        
        self.assertTrue(result['success'])
        self.assertEqual(self.game.board[5][4], ' ')
        self.assertEqual(self.game.board[2][4], ' ')
        self.assertEqual(self.game.board[1][4], 'w')
        self.assertEqual(self.game.current_player, 'B')

    def test_game_over_when_blocked(self):
        """
        NİHAİ TEST: Bir oyuncunun hamlesi kalmadığında oyunun bitmesini test eder.
        DÜZELTME: Siyah taşın zıplayacağı yerler de doldurularak tamamen bloke edildi.
        """
        self.game.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.game.board[0][0] = 'B'
        self.game.board[1][0] = 'W'
        self.game.board[0][1] = 'W'
        self.game.board[2][0] = 'W'
        self.game.board[0][2] = 'W'
        self.game.board[7][7] = 'W'
        
        self.game.current_player = 'B'
        self.game.game_over = False
        
        self.game._check_game_over()
        
        self.assertTrue(self.game.game_over, "Siyah'ın hamlesi olmadığı için oyun bitmeli.")
        self.assertEqual(self.game.winner, 'W', "Kazanan Beyaz olmalı.")

if __name__ == '__main__':
    unittest.main()
