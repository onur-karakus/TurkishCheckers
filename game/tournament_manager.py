# game/tournament_manager.py
"""
Turnuva yöneticisi. Artık her maç için pozisyon geçmişini tutar ve
tekrar kuralını uygular.
"""
from core import rules, notation
from ai.ai_player import AIPlayer
import random
import copy

class TournamentManager:
    def __init__(self):
        self.players, self.schedule, self.scores = {}, [], {}
        self.current_match_index, self.is_running, self.board = -1, False, None
        self.current_game_over, self.current_winner_color = False, None
        self.move_count, self.move_history, self.board_history = 0, [], []

    def start_tournament(self):
        self.players = {
            "Kolay": AIPlayer('white', time_limit_seconds=1),
            "Orta": AIPlayer('white', time_limit_seconds=3),
            "Zor": AIPlayer('white', time_limit_seconds=5)
        }
        player_names = list(self.players.keys())
        self.scores = {name: {'wins': 0, 'draws': 0, 'losses': 0, 'points': 0.0} for name in player_names}
        self.schedule = []
        for i in range(len(player_names)):
            for j in range(i + 1, len(player_names)):
                p1, p2 = player_names[i], player_names[j]
                self.schedule.append({'white': p1, 'black': p2, 'result': None, 'move_count': 0})
                self.schedule.append({'white': p2, 'black': p1, 'result': None, 'move_count': 0})
        self.is_running, self.current_match_index = True, -1
        self.next_match()

    def next_match(self):
        self.current_match_index += 1
        if self.current_match_index >= len(self.schedule):
            self.is_running, self.current_game_over = False, True
            return
        self.board = [[0] * 8 for _ in range(8)]
        for i in range(8):
            self.board[1][i], self.board[2][i] = 2, 2
            self.board[5][i], self.board[6][i] = 1, 1
        self.current_player_color, self.current_game_over, self.current_winner_color = 'white', False, None
        self.move_count, self.move_history, self.board_history = 0, [], [copy.deepcopy(self.board)]

    def play_next_ai_move(self):
        if self.current_game_over: self.next_match()
        if not self.is_running: return
        match_info = self.schedule[self.current_match_index]
        player_name = match_info[self.current_player_color]
        active_player = self.players[player_name]
        active_player.player_color = self.current_player_color
        possible_moves, _ = rules.get_all_valid_moves(self.board, self.current_player_color, self.board_history)
        if not possible_moves:
            self.end_current_game()
            return
        ai_move_obj = active_player.get_move(self.board, self.board_history)
        if not ai_move_obj:
            self.end_current_game()
            return
        move = None
        ai_path_tuple = ai_move_obj['path']
        for m in possible_moves:
            if tuple(m['path']) == ai_path_tuple:
                move = m
                break
        if not move: move = random.choice(possible_moves)
        self.move_history.append(notation.to_dama_notation(move))
        self.board = rules._simulate_move(self.board, move)
        self.board_history.append(copy.deepcopy(self.board))
        self.current_player_color = 'black' if self.current_player_color == 'white' else 'white'
        self.move_count += 0.5
        self._check_game_over()

    def _check_game_over(self):
        white_pieces = sum(row.count(1) + row.count(3) for row in self.board)
        black_pieces = sum(row.count(2) + row.count(4) for row in self.board)
        if white_pieces == 0: self.end_current_game('black')
        elif black_pieces == 0: self.end_current_game('white')
        elif self.move_count > 150: self.end_current_game('draw')
        else:
            moves, _ = rules.get_all_valid_moves(self.board, self.current_player_color, self.board_history)
            if not moves:
                winner = 'black' if self.current_player_color == 'white' else 'white'
                self.end_current_game(winner)

    def end_current_game(self, winner_color=None):
        self.current_game_over = True
        self.current_winner_color = winner_color
        if self.current_match_index >= len(self.schedule): return
        match_info = self.schedule[self.current_match_index]
        white_player_name, black_player_name = match_info['white'], match_info['black']
        winner_name = None
        if winner_color == 'white':
            winner_name = white_player_name
            self.scores[white_player_name]['wins'] += 1; self.scores[white_player_name]['points'] += 1.0
            self.scores[black_player_name]['losses'] += 1
        elif winner_color == 'black':
            winner_name = black_player_name
            self.scores[black_player_name]['wins'] += 1; self.scores[black_player_name]['points'] += 1.0
            self.scores[white_player_name]['losses'] += 1
        else:
            winner_name = "Berabere"
            self.scores[white_player_name]['draws'] += 1; self.scores[white_player_name]['points'] += 0.5
            self.scores[black_player_name]['draws'] += 1; self.scores[black_player_name]['points'] += 0.5
        self.schedule[self.current_match_index]['result'] = winner_name
        self.schedule[self.current_match_index]['move_count'] = int(self.move_count)
    
    def _get_evaluation_percentage(self):
        if self.board is None: return 50.0
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

    def get_state(self):
        return {
            'isRunning': self.is_running, 'board': self.board, 'scores': self.scores,
            'schedule': self.schedule, 'currentMatchIndex': self.current_match_index,
            'isGameOver': self.current_game_over, 'winner': self.current_winner_color,
            'turn': self.current_player_color, 'evaluation': self._get_evaluation_percentage(),
            'move_history': self.move_history
        }
