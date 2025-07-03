# TurkishCheckers/game/game_manager.py
from core import rules, board as board_utils, notation
from ai.intelligence import MinimaxEngine
from ai.ai_player import get_default_ai_weights

class GameManager:
    MAX_MOVES_NO_CAPTURE = 40

    def __init__(self):
        self.board = board_utils.setup_new_board()
        self.current_player = 'W'
        self.game_over = True
        self.is_active = False
        self.winner = None
        self.message = "Yeni bir oyuna başlamak için ayarları seçin."
        self.history = []
        self.move_notations = []
        self.moves_since_last_capture = 0
        self.last_move_path = None
        self.captured_pieces_this_turn = []
        
        self.mode = 'pve'
        self.player_color = 'W'
        self.ai_player_color = 'B'
        self.difficulty = 50
        self.ai_time_limit = 3.5
        self.ai_weights = get_default_ai_weights()

        self.time_white = None
        self.time_black = None
        self.increment = 0
        self.time_control_active = False

        self.ai_engine = MinimaxEngine()

    def setup_new_game(self, mode='pve', player_color='W', difficulty=50, time_control='unlimited'):
        self.board = board_utils.setup_new_board()
        self.current_player = 'W'
        self.game_over = True
        self.is_active = False
        self.winner = None
        self.message = "Yeni bir oyuna başlamak için ayarları seçin."
        self.history = [[row[:] for row in self.board]]
        self.move_notations = []
        self.moves_since_last_capture = 0
        self.last_move_path = None
        
        self.mode = mode
        self.difficulty = difficulty
        if mode == 'pve':
            self.player_color = player_color
            self.ai_player_color = rules.get_opponent(player_color)
            self.ai_time_limit = self._difficulty_to_time_limit(difficulty)
        
        self._setup_time_control(time_control)

    def start_game(self):
        self.game_over = False
        self.is_active = True
        self.message = "Oyun Başladı! Sıra Beyaz'da."

    def resign(self):
        self.game_over = True
        self.is_active = False
        self.winner = rules.get_opponent(self.current_player)
        self.message = f"{'Beyaz' if self.current_player == 'W' else 'Siyah'} oyunu terk etti."

    def request_ai_move(self):
        if not self.is_active or self.game_over: return None
        # DÜZELTME: Artık gereksiz olan transposition_table argümanı kaldırıldı.
        return self.ai_engine.get_computer_move(self.board, self.current_player, self.ai_weights, self.ai_time_limit)

    def get_engine_analysis(self):
        if not self.is_active or self.game_over: return None
        analysis_time_limit = self.ai_time_limit if self.mode == 'pve' else 3.0
        return self.ai_engine.get_evaluation_and_top_moves(self.board, self.current_player, self.ai_weights, analysis_time_limit)

    def _apply_move(self, path, move_type):
        self.captured_pieces_this_turn = []
        if move_type == "capture":
            rules.apply_capture_on_board(path, self.board, self.captured_pieces_this_turn)
            self.moves_since_last_capture = 0
        else:
            rules.apply_normal_move_on_board(path[0], path[1], self.board)
            self.moves_since_last_capture += 1

        self.history.append([row[:] for row in self.board])
        self.last_move_path = path
        move_note = notation.path_to_notation(path, move_type)
        if move_note: self.move_notations.append(move_note)
        if move_type == "capture":
            end_pos = path[-1]
            piece = self.board[end_pos[0]][end_pos[1]]
            more_captures = rules.find_captures_for_piece(end_pos[0], end_pos[1], self.board, piece.islower())
            if more_captures:
                self.message = "Zorunlu alım devam ediyor. Tekrar oynamalısınız!"
                return
        self.switch_player()
        self.check_game_over()
        
    @classmethod
    def from_dict(cls, data):
        game = cls()
        for key, value in data.items():
            if hasattr(game, key):
                setattr(game, key, value)
        
        if game.mode == 'pve':
            game.ai_time_limit = game._difficulty_to_time_limit(game.difficulty)
            game.ai_player_color = rules.get_opponent(game.player_color)

        return game

    def _difficulty_to_time_limit(self, difficulty):
        min_seconds = 1.0; max_seconds = 6.0
        return min_seconds + (difficulty / 100.0) * (max_seconds - min_seconds)
    def play_turn(self, start_pos, end_pos):
        piece = self.board[start_pos[0]][start_pos[1]]
        if not piece or piece.upper() != self.current_player: return {"success": False, "message": "Geçersiz hamle: Size ait olmayan bir taş."}
        possible_moves = rules.get_all_possible_moves(self.current_player, self.board)
        move_to_apply = next((p for p in possible_moves["moves"] if p[0] == start_pos and p[-1] == end_pos), None)
        if not move_to_apply and possible_moves["type"] == "capture":
            move_to_apply = next((p for p in possible_moves["moves"] if p[0] == start_pos and p[1] == end_pos), None)
            if move_to_apply: move_to_apply = [move_to_apply[0], move_to_apply[1]]
        if not move_to_apply:
            message = "Geçersiz hamle." + (" Zorunlu taş alma hamlesi var!" if possible_moves["type"] == "capture" else "")
            return {"success": False, "message": message}
        self._apply_move(move_to_apply, possible_moves["type"])
        return {"success": True, "path": move_to_apply, "type": possible_moves["type"]}
    def switch_player(self):
        self.current_player = rules.get_opponent(self.current_player)
        self.message = f"Sıra {'Beyaz' if self.current_player == 'W' else 'Siyah'}'da."
    def check_game_over(self):
        if self.game_over: return True
        is_over, winner = rules.is_game_over(self.board, self.current_player)
        if is_over:
            message = f"Oyun Bitti! Kazanan: {'Beyaz' if winner == 'W' else 'Siyah'}."
            if not board_utils.count_pieces(self.board)[0] or not board_utils.count_pieces(self.board)[1]:
                message += " (Tüm taşlar alındı)."
            else:
                message += " (Rakip bloke oldu)."
            self._end_game(winner, message)
            return True
        if self.time_control_active:
            if self.time_white is not None and self.time_white <= 0: self._end_game('B', "Oyun Bitti! Beyaz'ın süresi doldu."); return True
            if self.time_black is not None and self.time_black <= 0: self._end_game('W', "Oyun Bitti! Siyah'ın süresi doldu."); return True
        if self.moves_since_last_capture >= self.MAX_MOVES_NO_CAPTURE: self._end_game(None, f"Oyun Berabere! ({self.MAX_MOVES_NO_CAPTURE} hamledir taş alınmadı)."); return True
        return False
    def get_valid_moves_for_piece(self, r, c):
        all_possible = rules.get_all_possible_moves(self.current_player, self.board)
        return [path[-1] for path in all_possible["moves"] if path[0] == (r, c)]
    def update_time(self, time_left):
        time_key = f"time_{self.current_player.lower()}"; setattr(self, time_key, time_left)
        if self.increment > 0: current_time = getattr(self, time_key); setattr(self, time_key, current_time + self.increment)
    def handle_timeout(self):
        time_key = f"time_{self.current_player.lower()}"; setattr(self, time_key, 0); self.check_game_over()
    def _end_game(self, winner, message):
        self.game_over = True; self.is_active = False; self.winner = winner; self.message = message
    def _setup_time_control(self, time_control_str):
        if self.mode == 'pvp' and time_control_str != 'unlimited':
            self.time_control_active = True; parts = time_control_str.split('_'); self.time_white = int(parts[0]); self.time_black = int(parts[0]); self.increment = int(parts[1]) if len(parts) > 1 else 0
        else:
            self.time_control_active = False; self.time_white = None; self.time_black = None; self.increment = 0
    def to_dict(self):
        mandatory_squares = []
        if self.is_active and not self.game_over:
            possible_moves = rules.get_all_possible_moves(self.current_player, self.board)
            if possible_moves['type'] == 'capture': mandatory_squares = list(set([move[0] for move in possible_moves['moves']]))
        return {'board': self.board, 'current_player': self.current_player, 'game_over': self.game_over, 'is_active': self.is_active, 'winner': self.winner, 'message': self.message, 'history': self.history, 'move_notations': self.move_notations, 'last_move_path': self.last_move_path, 'mandatory_capture_squares': mandatory_squares, 'mode': self.mode, 'player_color': self.player_color, 'difficulty': self.difficulty, 'time_white': self.time_white, 'time_black': self.time_black, 'increment': self.increment, 'time_control_active': self.time_control_active}
