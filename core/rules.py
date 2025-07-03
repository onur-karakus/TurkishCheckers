# TurkishCheckers/core/rules.py
from . import board as board_utils

def get_opponent(player):
    """Verilen oyuncunun rakibini döndürür."""
    return 'B' if player.upper() == 'W' else 'W'

def get_all_possible_moves(player, board_state):
    """
    Bir oyuncu için tüm olası hamleleri hesaplar.
    Türk Daması kurallarına göre, taş alma hamlesi varsa, sadece en çok taşı alan
    hamleler geçerlidir.
    """
    all_captures = []
    for r in range(board_utils.BOARD_SIZE):
        for c in range(board_utils.BOARD_SIZE):
            piece = board_state[r][c]
            if piece != board_utils.EMPTY_SQUARE and piece.upper() == player:
                captures_for_piece = find_captures_for_piece(r, c, board_state, piece.islower())
                if captures_for_piece:
                    all_captures.extend(captures_for_piece)
    
    if all_captures:
        max_len = 0
        for path in all_captures:
            if len(path) > max_len:
                max_len = len(path)
        
        longest_captures = [path for path in all_captures if len(path) == max_len]
        return {"type": "capture", "moves": longest_captures}

    all_normal_moves = []
    for r in range(board_utils.BOARD_SIZE):
        for c in range(board_utils.BOARD_SIZE):
            piece = board_state[r][c]
            if piece != board_utils.EMPTY_SQUARE and piece.upper() == player:
                normal_moves_for_piece = find_normal_moves_for_piece(r, c, board_state, piece.islower())
                if normal_moves_for_piece:
                    all_normal_moves.extend(normal_moves_for_piece)

    return {"type": "normal", "moves": all_normal_moves}

def find_captures_for_piece(r, c, board_state, is_dama):
    """
    Belirli bir taştan başlayarak tüm olası taş alma dizilerini (yollarını) özyineli olarak bulur.
    """
    paths = []
    piece_char = board_state[r][c]
    
    def find_recursive(path, current_board):
        row, col = path[-1]
        has_more_captures = False
        
        if not is_dama:
            fwd = -1 if piece_char.upper() == 'W' else 1
            capture_directions = [(fwd, 0), (0, -1), (0, 1)]

            for dr, dc in capture_directions:
                enemy_r, enemy_c = row + dr, col + dc
                jump_r, jump_c = row + 2 * dr, col + 2 * dc
                
                if board_utils.is_within_bounds(jump_r, jump_c) and board_utils.is_within_bounds(enemy_r, enemy_c):
                    enemy_piece = current_board[enemy_r][enemy_c]
                    jump_square = current_board[jump_r][jump_c]
                    
                    if enemy_piece.upper() == get_opponent(piece_char) and jump_square == board_utils.EMPTY_SQUARE:
                        temp_board = [b[:] for b in current_board]
                        temp_board[jump_r][jump_c] = piece_char
                        temp_board[row][col] = board_utils.EMPTY_SQUARE
                        temp_board[enemy_r][enemy_c] = board_utils.EMPTY_SQUARE
                        has_more_captures = True
                        find_recursive(path + [(jump_r, jump_c)], temp_board)
        else: # Dama için taş alma mantığı
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                first_piece_pos = None
                for i in range(1, board_utils.BOARD_SIZE):
                    scan_r, scan_c = row + i * dr, col + i * dc
                    if not board_utils.is_within_bounds(scan_r, scan_c): break
                    if current_board[scan_r][scan_c] != board_utils.EMPTY_SQUARE:
                        first_piece_pos = (scan_r, scan_c)
                        break
                
                if first_piece_pos:
                    enemy_r, enemy_c = first_piece_pos
                    if current_board[enemy_r][enemy_c].upper() == get_opponent(piece_char):
                        for j in range(1, board_utils.BOARD_SIZE):
                            jump_r, jump_c = enemy_r + j * dr, enemy_c + j * dc
                            if not board_utils.is_within_bounds(jump_r, jump_c): break
                            
                            if current_board[jump_r][jump_c] == board_utils.EMPTY_SQUARE:
                                temp_board = [b[:] for b in current_board]
                                temp_board[jump_r][jump_c] = piece_char
                                temp_board[row][col] = board_utils.EMPTY_SQUARE
                                temp_board[enemy_r][enemy_c] = board_utils.EMPTY_SQUARE
                                has_more_captures = True
                                find_recursive(path + [(jump_r, jump_c)], temp_board)
                            else:
                                break
        
        if not has_more_captures and len(path) > 1:
            paths.append(path)

    find_recursive([(r, c)], [row[:] for row in board_state])
    return paths

def find_normal_moves_for_piece(r, c, board_state, is_dama):
    moves = []
    piece = board_state[r][c]
    
    if not is_dama:
        fwd = -1 if piece.upper() == 'W' else 1
        directions = [(fwd, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if board_utils.is_within_bounds(nr, nc) and board_state[nr][nc] == board_utils.EMPTY_SQUARE:
                moves.append([(r, c), (nr, nc)])
    else: # Dama hareketi
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            for i in range(1, board_utils.BOARD_SIZE):
                nr, nc = r + i * dr, c + i * dc
                if not board_utils.is_within_bounds(nr, nc):
                    break
                if board_state[nr][nc] == board_utils.EMPTY_SQUARE:
                    moves.append([(r, c), (nr, nc)])
                else:
                    break
    return moves

def apply_capture_on_board(path, board_state, captured_pieces_list=None):
    start_r, start_c = path[0]
    end_r, end_c = path[-1]
    piece = board_state[start_r][start_c]
    
    board_state[start_r][start_c] = board_utils.EMPTY_SQUARE
    
    for i in range(len(path) - 1):
        r1, c1 = path[i]; r2, c2 = path[i+1]
        dr = (r2 - r1) // abs(r2 - r1) if r1 != r2 else 0
        dc = (c2 - c1) // abs(c2 - c1) if c1 != c2 else 0
        tr, tc = r1 + dr, c1 + dc
        while (tr, tc) != (r2, c2):
            if board_state[tr][tc] != board_utils.EMPTY_SQUARE:
                if captured_pieces_list is not None:
                    captured_pieces_list.append(board_state[tr][tc])
                board_state[tr][tc] = board_utils.EMPTY_SQUARE
                break
            tr += dr; tc += dc
            
    board_state[end_r][end_c] = piece
    _promote_if_needed(end_r, end_c, board_state)

def apply_normal_move_on_board(start_pos, end_pos, board_state):
    piece = board_state[start_pos[0]][start_pos[1]]
    board_state[start_pos[0]][start_pos[1]] = board_utils.EMPTY_SQUARE
    board_state[end_pos[0]][end_pos[1]] = piece
    _promote_if_needed(end_pos[0], end_pos[1], board_state)

def _promote_if_needed(r, c, board_state):
    piece = board_state[r][c]
    if piece == board_utils.WHITE_PIECE and r == 0:
        board_state[r][c] = board_utils.WHITE_DAMA
    if piece == board_utils.BLACK_PIECE and r == 7:
        board_state[r][c] = board_utils.BLACK_DAMA

def is_player_blocked(player, board_state):
    """Bir oyuncunun geçerli hamlesi kalıp kalmadığını kontrol eder."""
    return not get_all_possible_moves(player, board_state)["moves"]

def is_game_over(board_state, current_player):
    """
    Oyunun bitip bitmediğini ve kazananı kontrol eder.
    Bu fonksiyon, sunucu çökmesini önlemek için gereklidir.
    """
    w_pieces, b_pieces = board_utils.count_pieces(board_state)
    if w_pieces == 0:
        return True, 'B' # Beyazın taşı kalmadı, Siyah kazandı
    if b_pieces == 0:
        return True, 'W' # Siyahın taşı kalmadı, Beyaz kazandı
    
    # Sıradaki oyuncunun hamlesi yoksa, rakip kazanır.
    if is_player_blocked(current_player, board_state):
        return True, get_opponent(current_player)

    # Oyun bitmediyse
    return False, None
