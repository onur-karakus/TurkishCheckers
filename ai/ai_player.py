# ai/ai_player.py
"""
Yapay zeka motoru. 
(TypeError: unexpected keyword argument 'time_limit_seconds' hatası düzeltildi)
"""
import math
import random
import copy
import time
import numpy as np
from core import rules

# --- Stratejik Değerlendirme Sabitleri ---
MATERIAL_SCORES = {1: 100, 2: -100, 3: 500, 4: -500}
MAN_PST_WHITE = [
    [200, 200, 200, 200, 200, 200, 200, 200], [ 70,  80,  90,  90,  90,  90,  80,  70],
    [ 50,  60,  70,  70,  70,  70,  60,  50], [ 30,  40,  50,  50,  50,  50,  40,  30],
    [ 15,  20,  30,  30,  30,  30,  20,  15], [  5,  10,  15,  15,  15,  15,  10,   5],
    [  0,   0,   0,   0,   0,   0,   0,   0], [  0,   0,   0,   0,   0,   0,   0,   0]
]
MAN_PST_BLACK = MAN_PST_WHITE[::-1]
KING_PST = [
    [ 10,  20,  20,  20,  20,  20,  20,  10], [ 20,  30,  35,  35,  35,  35,  30,  20],
    [ 20,  35,  45,  50,  50,  45,  35,  20], [ 20,  35,  50,  60,  60,  50,  35,  20],
    [ 20,  35,  50,  60,  60,  50,  35,  20], [ 20,  35,  45,  50,  50,  45,  35,  20],
    [ 20,  30,  35,  35,  35,  35,  30,  20], [ 10,  20,  20,  20,  20,  20,  20,  10]
]

class MCTSNode:
    def __init__(self, parent=None, prior_p=1.0):
        self.parent, self.children, self.visit_count, self.total_value, self.prior_probability = parent, {}, 0, 0.0, prior_p
    def expand(self, policy):
        for move_tuple, prob in policy.items():
            if move_tuple not in self.children: self.children[move_tuple] = MCTSNode(parent=self, prior_p=prob)
    def select(self, c_puct):
        best_score, best_action = -float('inf'), None
        for action, node in self.children.items():
            score = (1.0 - (node.total_value / (node.visit_count + 1e-5))) + c_puct * node.prior_probability * math.sqrt(self.visit_count) / (1 + node.visit_count)
            if score > best_score: best_score, best_action = score, action
        return best_action, self.children[best_action]
    def backup(self, value):
        if self.parent: self.parent.backup(-value)
        self.visit_count += 1
        self.total_value += value

class AIPlayer:
    # --- BAŞLANGIÇ: Hata Düzeltmesi ---
    # __init__ metodu artık 'time_limit_seconds' parametresini kabul ediyor.
    def __init__(self, player_color, time_limit_seconds=5, c_puct=1.25):
        self.player_color = player_color
        self.time_limit_seconds = time_limit_seconds
        self.c_puct = c_puct
    # --- SON: Hata Düzeltmesi ---

    def _advanced_evaluation(self, board):
        if self._is_game_over(board):
            winner = self._get_winner(board)
            if winner == 'white': return 10000
            if winner == 'black': return -10000
            return 0
        score, total_pieces = 0, 0
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece == 0: continue
                total_pieces += 1
                score += MATERIAL_SCORES.get(piece, 0)
                if piece == 1: score += MAN_PST_WHITE[r][c]
                elif piece == 2: score -= MAN_PST_BLACK[r][c]
                elif piece == 3: score += KING_PST[r][c]
                elif piece == 4: score -= KING_PST[r][c]
        if total_pieces < 10:
             material_score = sum(MATERIAL_SCORES.get(p, 0) for row in board for p in row)
             score = (score * 0.4) + (material_score * 0.6)
        return score

    def _get_policy_and_value(self, board, player_color, board_history):
        possible_moves, _ = rules.get_all_valid_moves(board, player_color, board_history)
        if not possible_moves: return {}, 0.0
        move_scores = {}
        for move in possible_moves:
            temp_board = self._simulate_move(board, move)
            score = self._advanced_evaluation(temp_board)
            if player_color == 'black': score = -score
            move_scores[tuple(move['path'])] = score
        if not move_scores: return {}, 0.0
        scores = np.array(list(move_scores.values()))
        scores -= np.max(scores)
        exp_scores = np.exp(scores / 100)
        probs = exp_scores / (np.sum(exp_scores) + 1e-5)
        policy = {path_tuple: prob for path_tuple, prob in zip(move_scores.keys(), probs)}
        value = self._advanced_evaluation(board)
        normalized_value = math.tanh(value / 1000.0)
        return policy, normalized_value

    def get_move(self, board, board_history):
        root = MCTSNode()
        policy, _ = self._get_policy_and_value(board, self.player_color, board_history)
        if not policy: return None
        root.expand(policy)
        start_time = time.time()
        num_simulations = 0
        while time.time() - start_time < self.time_limit_seconds:
            node, temp_board, current_player = root, copy.deepcopy(board), self.player_color
            temp_history = copy.deepcopy(board_history)
            while node.children:
                action, node = node.select(self.c_puct)
                temp_board = self._simulate_move(temp_board, {'path': list(action)})
                temp_history.append(temp_board)
                current_player = 'white' if current_player == 'black' else 'black'
            policy, value = self._get_policy_and_value(temp_board, current_player, temp_history)
            if not self._is_game_over(temp_board):
                node.expand(policy)
            if current_player == 'black': value = -value
            node.backup(value)
            num_simulations += 1
        print(f"AI ({self.player_color}) completed {num_simulations} simulations in {time.time() - start_time:.2f} seconds.")
        if not root.children: return None
        best_action = max(root.children.items(), key=lambda item: item[1].visit_count)[0]
        return {'path': best_action}

    def _simulate_move(self, board, move):
        new_board = copy.deepcopy(board)
        if 'path' not in move or not move['path']: return new_board
        start_pos, end_pos = move['path'][0], move['path'][-1]
        if not (0 <= start_pos[0] < 8 and 0 <= start_pos[1] < 8): return new_board
        piece = new_board[start_pos[0]][start_pos[1]]
        if piece == 0: return new_board
        player = rules.get_piece_color(piece)
        new_board[start_pos[0]][start_pos[1]] = 0
        promoted_piece = piece
        if player == 'white' and end_pos[0] == 0: promoted_piece = 3
        elif player == 'black' and end_pos[0] == 7: promoted_piece = 4
        new_board[end_pos[0]][end_pos[1]] = promoted_piece
        if 'captured' in move:
            for r, c in move['captured']: new_board[r][c] = 0
        return new_board
        
    def _is_game_over(self, board): return self._get_winner(board) is not None
    def _get_winner(self, board):
        white_pieces = sum(row.count(1) + row.count(3) for row in board)
        black_pieces = sum(row.count(2) + row.count(4) for row in board)
        if white_pieces == 0: return 'black'
        if black_pieces == 0: return 'white'
        white_moves, _ = rules.get_all_valid_moves(board, 'white')
        if not white_moves: return 'black'
        black_moves, _ = rules.get_all_valid_moves(board, 'black')
        if not black_moves: return 'white'
        return None
