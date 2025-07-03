# TurkishCheckers/ai/intelligence.py
import math
import random
import time
from core import rules, notation, board as board_utils

class MinimaxEngine:
    """
    YÜKSELTME: Bu sürüm, ham puanları Leela Chess Zero benzeri bir kazanma
    olasılığına çevirerek daha sezgisel bir skorlama sunar.
    """
    def __init__(self):
        self.start_time = 0
        self.time_limit = 0
        self.nodes_searched = 0
        self.transposition_table = {}

    def _convert_score_to_win_percentage(self, score):
        """
        Ham değerlendirme puanını (centipawn) %0-100 arası bir kazanma
        olasılığına çevirir.
        """
        if score > 9000: return 100.0
        if score < -9000: return 0.0
        
        # DÜZELTME: Ölçekleme faktörü, küçük avantajların olasılığa daha
        # hassas bir şekilde yansıması için güncellendi.
        SCALING_FACTOR = 150.0
        return 100.0 / (1 + math.exp(-score / SCALING_FACTOR))

    def _is_time_up(self):
        return time.time() - self.start_time > self.time_limit

    def _get_next_board_state(self, board_state, move_path, move_type):
        temp_board = [row[:] for row in board_state]
        if move_type == 'capture':
            rules.apply_capture_on_board(move_path, temp_board)
        else:
            rules.apply_normal_move_on_board(move_path[0], move_path[1], temp_board)
        return temp_board

    def _search(self, board_state, depth, alpha, beta, is_maximizing_player, current_player, root_player, weights):
        if self._is_time_up():
            return 0, None

        self.nodes_searched += 1
        
        is_terminal, winner = rules.is_game_over(board_state, current_player)

        if depth == 0 or is_terminal:
            if is_terminal:
                if winner == root_player: return (10000 + depth, None)
                if winner == rules.get_opponent(root_player): return (-10000 - depth, None)
                return (0, None)
            return self.evaluate_board(board_state, root_player, weights), None

        board_tuple = tuple(map(tuple, board_state))
        tt_key = (board_tuple, depth, current_player)
        if tt_key in self.transposition_table:
            return self.transposition_table[tt_key]

        best_move = None
        possible_moves = rules.get_all_possible_moves(current_player, board_state)
        
        if not possible_moves['moves']:
             return (-10000 - depth, None) if is_maximizing_player else (10000 + depth, None)

        if is_maximizing_player:
            max_eval = -math.inf
            for move_path in possible_moves['moves']:
                next_board = self._get_next_board_state(board_state, move_path, possible_moves['type'])
                evaluation, _ = self._search(next_board, depth - 1, alpha, beta, False, rules.get_opponent(current_player), root_player, weights)
                if self._is_time_up(): break
                if evaluation > max_eval:
                    max_eval = evaluation
                    best_move = move_path
                alpha = max(alpha, evaluation)
                if beta <= alpha: break
            self.transposition_table[tt_key] = (max_eval, best_move)
            return max_eval, best_move
        else:
            min_eval = math.inf
            for move_path in possible_moves['moves']:
                next_board = self._get_next_board_state(board_state, move_path, possible_moves['type'])
                evaluation, _ = self._search(next_board, depth - 1, alpha, beta, True, rules.get_opponent(current_player), root_player, weights)
                if self._is_time_up(): break
                if evaluation < min_eval:
                    min_eval = evaluation
                    best_move = move_path
                beta = min(beta, evaluation)
                if beta <= alpha: break
            self.transposition_table[tt_key] = (min_eval, best_move)
            return min_eval, best_move
    
    def _iterative_deepening_search(self, board_state, player, weights, time_limit):
        self.start_time = time.time()
        self.time_limit = time_limit
        self.nodes_searched = 0
        self.transposition_table = {}
        depth = 1
        best_move_overall = None

        while not self._is_time_up():
            _, move = self._search(board_state, depth, -math.inf, math.inf, True, player, player, weights)
            if not self._is_time_up():
                best_move_overall = move
            else:
                break
            depth += 1
        return best_move_overall

    def get_computer_move(self, board_state, current_player, ai_weights, time_limit):
        best_move_path = self._iterative_deepening_search(board_state, current_player, ai_weights, time_limit)
        
        if not best_move_path:
            possible = rules.get_all_possible_moves(current_player, board_state)
            if not possible["moves"]: return None
            best_move_path = random.choice(possible["moves"])
            
        return {"move": (best_move_path[0], best_move_path[-1])}

    def get_evaluation_and_top_moves(self, board_state, player, weights, time_limit, num_moves=3):
        self.start_time = time.time()
        self.time_limit = time_limit
        self.nodes_searched = 0
        self.transposition_table = {}
        
        possible_moves = rules.get_all_possible_moves(player, board_state)
        if not possible_moves['moves']:
            return {"win_prob": 0.0, "top_moves": [], "nodes": 0}

        moves_with_scores = []
        depth = 1
        while not self._is_time_up():
             self._search(board_state, depth, -math.inf, math.inf, True, player, player, weights)
             if self._is_time_up(): break
             depth += 1

        for move_path in possible_moves['moves']:
            next_board = self._get_next_board_state(board_state, move_path, possible_moves['type'])
            score, _ = self._search(next_board, depth-1, -math.inf, math.inf, False, rules.get_opponent(player), player, weights)
            moves_with_scores.append({'move_path': move_path, 'score_raw': score, 'type': possible_moves['type']})
        
        moves_with_scores.sort(key=lambda x: x['score_raw'], reverse=True)
        
        top_moves_analysis = []
        overall_score_raw = moves_with_scores[0]['score_raw'] if moves_with_scores else -99999

        for item in moves_with_scores[:num_moves]:
            pv = self._get_principal_variation(board_state, player, item['move_path'], item['type'], depth)
            top_moves_analysis.append({
                "variation": " ".join(pv),
                "win_prob": self._convert_score_to_win_percentage(item['score_raw']),
                "move_path": item['move_path'] 
            })

        return {
            "win_prob": self._convert_score_to_win_percentage(overall_score_raw),
            "top_moves": top_moves_analysis,
            "nodes": self.nodes_searched
        }

    def _get_principal_variation(self, board, player, first_move_path, move_type, max_depth):
        pv = [notation.path_to_notation(first_move_path, move_type)]
        temp_board = self._get_next_board_state(board, first_move_path, move_type)
        current_player = rules.get_opponent(player)
        
        for i in range(max_depth - 1):
            board_tuple = tuple(map(tuple, temp_board))
            best_move = None
            for d in range(max_depth - i, 0, -1):
                key = (board_tuple, d, current_player)
                if key in self.transposition_table:
                    _, best_move = self.transposition_table[key]
                    if best_move: break
            
            if best_move:
                possible = rules.get_all_possible_moves(current_player, temp_board)
                current_move_type = 'normal'
                if possible['type'] == 'capture':
                    for capture_move in possible['moves']:
                        if capture_move == best_move:
                            current_move_type = 'capture'
                            break
                pv.append(notation.path_to_notation(best_move, current_move_type))
                temp_board = self._get_next_board_state(temp_board, best_move, current_move_type)
                current_player = rules.get_opponent(current_player)
            else:
                break
        return pv

    def evaluate_board(self, board_state, player_for_eval, weights):
        score = 0
        piece_value = weights.get('piece_value', 100)
        dama_value = weights.get('dama_value', 300)
        advancement_bonus = weights.get('advancement_bonus', 3)
        center_control_bonus = weights.get('center_control_bonus', 2)
        defensive_bonus = weights.get('defensive_bonus', 1.5)

        for r in range(8):
            for c in range(8):
                piece = board_state[r][c]
                if piece == ' ': continue
                is_player_piece = (piece.upper() == player_for_eval)
                current_piece_score = dama_value if piece.islower() else piece_value
                pos_bonus = 0
                if piece.upper() == 'W':
                    pos_bonus += (7 - r) * advancement_bonus
                    if r >= 4: pos_bonus += (r - 4) * defensive_bonus
                else:
                    pos_bonus += r * advancement_bonus
                    if r <= 3: pos_bonus += (3 - r) * defensive_bonus
                center_bonus = (3.5 - abs(3.5 - c)) * center_control_bonus
                current_piece_score += pos_bonus + center_bonus
                score += current_piece_score if is_player_piece else -current_piece_score
        return score
