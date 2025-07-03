# game_logic.py
from ai.intelligence import AIIntelligence
import math # Sigmoid fonksiyonu için eklendi

class Game:
    """
    Türk Daması oyununun temel kurallarını, durumunu ve akışını yöneten ana sınıf.
    NİHAİ REVİZYON: Tüm testleri geçecek ve sunucu çökmelerini önleyecek şekilde
    oyun mantığı tamamen yeniden yapılandırıldı ve kararlı hale getirildi.
    """
    def __init__(self):
        self.board = [[]]
        self.current_player = 'W'
        self.game_over = True
        self.winner = None
        self.message = "Oyun başlatılmadı."
        self.mode = 'pvp'
        self.player_color = None
        self.moves_since_last_capture = 0
        self.MAX_MOVES_NO_CAPTURE = 40
        self.last_move_path = None
        self.ai_logic = AIIntelligence(self)
        self.captured_pieces_this_turn = []
        self.history = []
        self.move_notations = []
        self.time_white = None
        self.time_black = None
        self.increment = 0
        self.difficulty = 50

    def setup_new_game(self, mode='pvp', player_color='W', initial_time=None, increment=0, difficulty=50):
        self.board = self._setup_board()
        self.current_player = 'W'
        self.game_over = False
        self.winner = None
        self.message = "Oyun Başladı! Sıra Beyaz'da."
        self.mode = mode
        self.player_color = player_color if mode == 'pve' else None
        self.moves_since_last_capture = 0
        self.last_move_path = None
        self.captured_pieces_this_turn = []
        self.history = [[row[:] for row in self.board]]
        self.move_notations = []
        self.time_white = initial_time
        self.time_black = initial_time
        self.increment = increment
        self.difficulty = difficulty

    def _setup_board(self):
        board = [[' ' for _ in range(8)] for _ in range(8)]
        for row in [5, 6]:
            for col in range(8):
                board[row][col] = 'W'
        for row in [1, 2]:
            for col in range(8):
                board[row][col] = 'B'
        return board
    
    def _to_algebraic(self, r, c):
        return f"{chr(ord('a') + c)}{8 - r}"

    def path_to_notation(self, path, move_type):
        if not path or len(path) < 2: return ""
        start_r, start_c = path[0]
        end_r, end_c = path[-1]
        separator = "x" if move_type == 'capture' else "-"
        return f"{self._to_algebraic(start_r, start_c)}{separator}{self._to_algebraic(end_r, end_c)}"

    def to_dict(self):
        mandatory_capture_squares = []
        if not self.game_over:
            possible_moves = self.get_all_possible_moves(self.current_player, self.board)
            if possible_moves['type'] == 'capture':
                mandatory_capture_squares = list(set([move[0] for move in possible_moves['moves']]))

        return {
            'board': self.board, 'current_player': self.current_player,
            'game_over': self.game_over, 'winner': self.winner,
            'message': self.message, 'mode': self.mode,
            'player_color': self.player_color, 'last_move_path': self.last_move_path,
            'captured_pieces_this_turn': self.captured_pieces_this_turn,
            'history': self.history,
            'move_notations': self.move_notations,
            'time_white': self.time_white,
            'time_black': self.time_black,
            'increment': self.increment,
            'difficulty': self.difficulty,
            'mandatory_capture_squares': mandatory_capture_squares
        }

    @classmethod
    def from_dict(cls, data):
        game = cls()
        for key, value in data.items():
            if hasattr(game, key):
                setattr(game, key, value)
        return game
    
    def get_opponent(self, player): return 'B' if player == 'W' else 'W'

    def find_captures_for_piece(self, r, c, board_state, is_dama):
        paths = []
        piece_char = board_state[r][c].upper()
        
        def find_recursive(path, current_board):
            row, col = path[-1]
            has_more_captures = False
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            
            if not is_dama:
                for dr, dc in directions:
                    if (piece_char == 'W' and dr > 0) or (piece_char == 'B' and dr < 0):
                        continue

                    enemy_r, enemy_c = row + dr, col + dc
                    jump_r, jump_c = row + 2 * dr, col + 2 * dc
                    
                    if 0 <= jump_r < 8 and 0 <= jump_c < 8 and \
                       0 <= enemy_r < 8 and 0 <= enemy_c < 8 and \
                       current_board[enemy_r][enemy_c].upper() == self.get_opponent(piece_char) and \
                       current_board[jump_r][jump_c] == ' ':
                        
                        temp_board = [b[:] for b in current_board]
                        temp_board[jump_r][jump_c] = current_board[row][col]
                        temp_board[row][col] = ' '
                        temp_board[enemy_r][enemy_c] = ' '
                        has_more_captures = True
                        find_recursive(path + [(jump_r, jump_c)], temp_board)
            else:
                for dr, dc in directions:
                    for i in range(1, 8):
                        enemy_r, enemy_c = row + i * dr, col + i * dc
                        if not (0 <= enemy_r < 8 and 0 <= enemy_c < 8): break
                        
                        piece_at_loc = current_board[enemy_r][enemy_c]
                        if piece_at_loc != ' ':
                            if piece_at_loc.upper() == self.get_opponent(piece_char):
                                for j in range(1, 8):
                                    jump_r, jump_c = enemy_r + j * dr, enemy_c + j * dc
                                    if not (0 <= jump_r < 8 and 0 <= jump_c < 8): break
                                    
                                    if current_board[jump_r][jump_c] == ' ':
                                        temp_board = [b[:] for b in current_board]
                                        temp_board[jump_r][jump_c] = current_board[row][col]
                                        temp_board[row][col] = ' '
                                        temp_board[enemy_r][enemy_c] = ' '
                                        has_more_captures = True
                                        find_recursive(path + [(jump_r, jump_c)], temp_board)
                                    else: break
                                break
                            break
            
            if not has_more_captures and len(path) > 1:
                paths.append(path)

        find_recursive([(r, c)], board_state)
        return paths

    def get_all_possible_moves(self, player, board_state):
        all_captures = []
        for r in range(8):
            for c in range(8):
                piece = board_state[r][c]
                if piece and piece.upper() == player:
                    captures = self.find_captures_for_piece(r, c, board_state, piece.islower())
                    if captures: all_captures.extend(captures)
        
        if all_captures:
            max_len = max(len(p) for p in all_captures)
            return {"type": "capture", "moves": [p for p in all_captures if len(p) == max_len]}

        all_normal_moves = []
        for r in range(8):
            for c in range(8):
                piece = board_state[r][c]
                if piece and piece.upper() == player:
                    if not piece.islower():
                        fwd = -1 if player == 'W' else 1
                        for dr, dc in [(fwd, 0), (0, -1), (0, 1)]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < 8 and 0 <= nc < 8 and board_state[nr][nc] == ' ':
                                all_normal_moves.append([(r, c), (nr, nc)])
                    else:
                        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                            for i in range(1, 8):
                                nr, nc = r + i * dr, c + i * dc
                                if 0 <= nr < 8 and 0 <= nc < 8:
                                    if board_state[nr][nc] == ' ':
                                        all_normal_moves.append([(r, c), (nr, nc)])
                                    else: break
                                else: break
        return {"type": "normal", "moves": all_normal_moves}

    def play_turn(self, start_pos, end_pos):
        piece = self.board[start_pos[0]][start_pos[1]]
        if not piece or piece.upper() != self.current_player:
            return {"success": False, "message": "Geçersiz hamle."}
        
        possible_moves = self.get_all_possible_moves(self.current_player, self.board)
        move_to_apply = next((p for p in possible_moves["moves"] if p[0] == start_pos and p[-1] == end_pos), None)
        
        if not move_to_apply and possible_moves["type"] == "capture":
            move_to_apply = next((p for p in possible_moves["moves"] if p[0] == start_pos and p[1] == end_pos), None)
            if move_to_apply:
                 move_to_apply = [move_to_apply[0], move_to_apply[1]]

        if not move_to_apply:
            message = "Geçersiz hamle." + (" Zorunlu taş alma hamlesi var!" if possible_moves["type"] == "capture" else "")
            return {"success": False, "message": message}
            
        return {"success": True, "path": move_to_apply, "type": possible_moves["type"]}

    def apply_move_from_path(self, path, move_type):
        self.captured_pieces_this_turn = []
        
        if move_type == "capture":
            self._apply_capture_on_board(path, self.board)
            self.moves_since_last_capture = 0
        else:
            self._apply_normal_move_on_board(path[0], path[1], self.board)
            self.moves_since_last_capture += 1

        self.history.append([row[:] for row in self.board])
        self.last_move_path = path
        # DÜZELTME: Notasyon kaydı geri eklendi.
        notation = self.path_to_notation(path, move_type)
        if notation: self.move_notations.append(notation)
        
        if move_type == "capture":
            end_pos = path[-1]
            is_dama = self.board[end_pos[0]][end_pos[1]].islower()
            more_captures = self.find_captures_for_piece(end_pos[0], end_pos[1], self.board, is_dama)
            if more_captures:
                self.message = "Zorunlu alım devam ediyor. Tekrar oynamalısınız!"
                return

        self.switch_player()
        self._check_game_over()

    def _promote_if_needed(self, r, c, board_state):
        piece = board_state[r][c]
        if piece == 'W' and r == 0: board_state[r][c] = 'w'
        if piece == 'B' and r == 7: board_state[r][c] = 'b'

    def _apply_normal_move_on_board(self, start_pos, end_pos, board_state):
        piece = board_state[start_pos[0]][start_pos[1]]
        board_state[start_pos[0]][start_pos[1]] = ' '
        board_state[end_pos[0]][end_pos[1]] = piece
        self._promote_if_needed(end_pos[0], end_pos[1], board_state)

    def _apply_capture_on_board(self, path, board_state):
        start_r, start_c = path[0]; end_r, end_c = path[-1]
        piece = board_state[start_r][start_c]
        board_state[start_r][start_c] = ' '
        for i in range(len(path) - 1):
            r1, c1 = path[i]; r2, c2 = path[i+1]
            dr = (r2 - r1) // abs(r2 - r1) if r1 != r2 else 0
            dc = (c2 - c1) // abs(c2 - c1) if c1 != c2 else 0
            tr, tc = r1 + dr, c1 + dc
            while tr != r2 or tc != c2:
                if board_state[tr][tc] != ' ':
                    if board_state is self.board: self.captured_pieces_this_turn.append(board_state[tr][tc])
                    board_state[tr][tc] = ' '
                    break
                tr += dr; tc += dc
        board_state[end_r][end_c] = piece
        self._promote_if_needed(end_r, end_c, board_state)
        
    def switch_player(self):
        self.current_player = self.get_opponent(self.current_player)
        self.message = f"Sıra {'Beyaz' if self.current_player == 'W' else 'Siyah'}'da."

    def _check_game_over(self):
        if self.game_over: return True

        w_pieces = sum(row.count('W') + row.count('w') for row in self.board)
        b_pieces = sum(row.count('B') + row.count('b') for row in self.board)
        if w_pieces == 0:
            self.game_over, self.winner, self.message = True, 'B', "Oyun Bitti! Siyah kazandı."
            return True
        if b_pieces == 0:
            self.game_over, self.winner, self.message = True, 'W', "Oyun Bitti! Beyaz kazandı."
            return True

        if self.is_terminal(self.board, self.current_player):
            self.game_over = True
            self.winner = self.get_opponent(self.current_player)
            self.message = f"Oyun Bitti! {'Beyaz' if self.winner == 'W' else 'Siyah'} kazandı. (Rakip bloke oldu)"
            return True
        
        if self.time_white is not None and self.time_white <= 0:
            self.game_over, self.winner, self.message = True, 'B', "Oyun Bitti! Beyaz'ın süresi doldu."
            return True
        if self.time_black is not None and self.time_black <= 0:
            self.game_over, self.winner, self.message = True, 'W', "Oyun Bitti! Siyah'ın süresi doldu."
            return True

        if self.moves_since_last_capture >= self.MAX_MOVES_NO_CAPTURE:
            self.game_over, self.winner, self.message = True, None, f"Oyun Berabere! {self.MAX_MOVES_NO_CAPTURE} hamledir taş alınmadı."
            return True
            
        return False

    def is_terminal(self, board_state, player):
        return not self.get_all_possible_moves(player, board_state)["moves"]

    def get_valid_moves_for_piece(self, r, c):
        all_possible = self.get_all_possible_moves(self.current_player, self.board)
        return [p[-1] for p in all_possible["moves"] if p[0] == (r, c)]

    def get_computer_move(self, ai_weights, search_depth=4):
        return self.ai_logic.get_computer_move(self.board, self.current_player, ai_weights, search_depth)

    def get_evaluation_and_top_moves(self, board_state, player, weights, depth, num_moves=3):
        return self.ai_logic.get_evaluation_and_top_moves(board_state, player, weights, depth, num_moves)
