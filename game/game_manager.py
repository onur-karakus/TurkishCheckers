# game/game_manager.py
"""
Oyun oturumlarını yönetir. Artık pozisyon geçmişini tutar ve
tekrar kuralını uygulamak için kullanır.
"""
from core import rules, notation
from ai.ai_player import AIPlayer
import copy

class GameManager:
    def __init__(self):
        self.current_difficulty = 'medium'
        self.move_history, self.board_history = [], []
        self.reset_game()

    def reset_game(self, difficulty='medium'):
        self.board = [[0] * 8 for _ in range(8)]
        for i in range(8):
            self.board[1][i], self.board[2][i] = 2, 2
            self.board[5][i], self.board[6][i] = 1, 1
        self.current_player, self.game_over, self.winner = 'white', False, None
        self.move_history, self.board_history = [], [copy.deepcopy(self.board)]
        self.current_difficulty = difficulty
        difficulty_settings = {'easy': 2, 'medium': 5, 'hard': 10}
        time_limit = difficulty_settings.get(difficulty, 5)
        self.ai_player = AIPlayer('black', time_limit_seconds=time_limit)
        self.valid_moves, self.is_capture = rules.get_all_valid_moves(self.board, self.current_player, self.board_history)

    def get_difficulty(self): return self.current_difficulty

    def get_state(self):
        white_pieces = sum(row.count(1) + row.count(3) for row in self.board)
        black_pieces = sum(row.count(2) + row.count(4) for row in self.board)
        return {
            'board': self.board, 'currentPlayer': self.current_player, 'gameOver': self.game_over,
            'winner': self.winner, 'validMoves': self.valid_moves, 'evaluation': self._get_evaluation_percentage(),
            'capturedByWhite': 16 - black_pieces, 'capturedByBlack': 16 - white_pieces, 'move_history': self.move_history
        }

    def make_move(self, move_data):
        if self.game_over: return False
        if 'path' not in move_data or not isinstance(move_data['path'], (list, tuple)) or not move_data['path']: return False
        try: client_path = tuple(move_data['path'])
        except (TypeError, ValueError): return False
        matched_move = None
        for m in self.valid_moves:
            if tuple(m['path']) == client_path:
                matched_move = m
                break
        if not matched_move: return False
        start_pos, end_pos = matched_move['path'][0], matched_move['path'][-1]
        piece = self.board[start_pos[0]][start_pos[1]]
        if rules.get_piece_color(piece) != self.current_player: return False
        self.move_history.append(notation.to_dama_notation(matched_move))
        self.board = rules._simulate_move(self.board, matched_move)
        self.board_history.append(copy.deepcopy(self.board))
        self._check_game_over()
        if not self.game_over: self._switch_player()
        return True

    def make_ai_move(self):
        if self.current_player == 'black' and not self.game_over:
            move_obj = self.ai_player.get_move(self.board, self.board_history)
            if move_obj: self.make_move(move_obj)
            else: self.game_over, self.winner = True, 'white'

    def _switch_player(self):
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        self.valid_moves, self.is_capture = rules.get_all_valid_moves(self.board, self.current_player, self.board_history)

    def _check_game_over(self):
        white_pieces = sum(row.count(1) + row.count(3) for row in self.board)
        black_pieces = sum(row.count(2) + row.count(4) for row in self.board)
        if white_pieces == 0: self.game_over, self.winner = True, 'black'
        elif black_pieces == 0: self.game_over, self.winner = True, 'white'
        elif white_pieces == 1 and black_pieces == 1: self.game_over, self.winner = True, 'draw'
        else:
            next_player = 'black' if self.current_player == 'white' else 'white'
            next_player_moves, _ = rules.get_all_valid_moves(self.board, next_player, self.board_history)
            if not next_player_moves: self.game_over, self.winner = True, self.current_player
    
    def _get_evaluation_percentage(self):
        white_score, black_score = 0, 0
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == 1: white_score += 1
                elif piece == 3: white_score += 5
                elif piece == 2: black_score += 1
                elif piece == 4: black_score += 5
        total_score = white_score + black_score
        if total_score == 0: return 50.0
        return (white_score / total_score) * 100
