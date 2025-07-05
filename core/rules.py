# core/rules.py
"""
Bu dosya Türk Daması oyununun temel kurallarını içerir.
(Üçlü tekrar kuralı denetimi eklendi)
"""
def get_piece_color(piece):
    if piece in [1, 3]: return 'white'
    if piece in [2, 4]: return 'black'
    return None

def is_king(piece):
    return piece in [3, 4]

def _simulate_move(board, move):
    """Bir hamleyi simüle eder ve yeni tahta durumunu döndürür."""
    new_board = [row[:] for row in board]
    start_pos, end_pos = move['path'][0], move['path'][-1]
    piece = new_board[start_pos[0]][start_pos[1]]
    player = get_piece_color(piece)
    new_board[start_pos[0]][start_pos[1]] = 0
    promoted_piece = piece
    if player == 'white' and end_pos[0] == 0: promoted_piece = 3
    elif player == 'black' and end_pos[0] == 7: promoted_piece = 4
    new_board[end_pos[0]][end_pos[1]] = promoted_piece
    for r, c in move.get('captured', []):
        new_board[r][c] = 0
    return new_board

def _find_captures_for_piece(board, r, c, is_king_piece, player, path, captured_so_far):
    sequences, has_more_captures = [], False
    forward_dir = -1 if player == 'white' else 1
    if not is_king_piece:
        capture_dirs = [[forward_dir, 0], [0, 1], [0, -1]]
        for dr, dc in capture_dirs:
            mid_r, mid_c = r + dr, c + dc
            end_r, end_c = r + 2 * dr, c + 2 * dc
            if 0 <= end_r < 8 and 0 <= end_c < 8 and board[end_r][end_c] == 0:
                mid_piece = board[mid_r][mid_c]
                if mid_piece != 0 and get_piece_color(mid_piece) != player and (mid_r, mid_c) not in captured_so_far:
                    new_board = [row[:] for row in board]
                    new_board[r][c], new_board[mid_r][mid_c] = 0, 0
                    new_path = path + [(end_r, end_c)]
                    new_captured = captured_so_far + [(mid_r, mid_c)]
                    continuations = _find_captures_for_piece(new_board, end_r, end_c, False, player, new_path, new_captured)
                    if continuations:
                        has_more_captures = True
                        sequences.extend(continuations)
                    else:
                        sequences.append({'path': new_path, 'captured': new_captured})
    else:
        all_dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dr, dc in all_dirs:
            for i in range(1, 8):
                check_r, check_c = r + i * dr, c + i * dc
                if not (0 <= check_r < 8 and 0 <= check_c < 8): break
                piece_on_path = board[check_r][check_c]
                if piece_on_path != 0:
                    if get_piece_color(piece_on_path) != player and (check_r, check_c) not in captured_so_far:
                        for j in range(1, 8):
                            end_r, end_c = check_r + j * dr, check_c + j * dc
                            if not (0 <= end_r < 8 and 0 <= end_c < 8): break
                            if board[end_r][end_c] != 0: break
                            new_board = [row[:] for row in board]
                            new_board[r][c], new_board[check_r][check_c] = 0, 0
                            new_path = path + [(end_r, end_c)]
                            new_captured = captured_so_far + [(check_r, check_c)]
                            continuations = _find_captures_for_piece(new_board, end_r, end_c, True, player, new_path, new_captured)
                            if continuations:
                                has_more_captures = True
                                sequences.extend(continuations)
                            else:
                                sequences.append({'path': new_path, 'captured': new_captured})
                    break 
    if not has_more_captures and captured_so_far:
        return [{'path': path, 'captured': captured_so_far}]
    return sequences

def get_all_valid_moves(board, player, board_history=None):
    """
    Sırası gelen oyuncu için tüm geçerli hamleleri hesaplar.
    Tekrar kuralını ihlal eden hamleleri filtreler.
    """
    all_captures = []
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece != 0 and get_piece_color(piece) == player:
                captures = _find_captures_for_piece(board, r, c, is_king(piece), player, [(r, c)], [])
                if captures:
                    all_captures.extend(captures)

    moves_to_filter = []
    is_capture = False
    if all_captures:
        max_captured = max(len(move['captured']) for move in all_captures)
        moves_to_filter = [move for move in all_captures if len(move['captured']) == max_captured]
        is_capture = True
    else:
        simple_moves = []
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece != 0 and get_piece_color(piece) == player:
                    if not is_king(piece):
                        forward = -1 if player == 'white' else 1
                        dirs = [[forward, 0], [0, 1], [0, -1]]
                        for dr, dc in dirs:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] == 0:
                                simple_moves.append({'path': [(r, c), (nr, nc)], 'captured': []})
                    else:
                        dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]]
                        for dr, dc in dirs:
                            for i in range(1, 8):
                                nr, nc = r + i * dr, c + i * dc
                                if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] == 0:
                                    simple_moves.append({'path': [(r, c), (nr, nc)], 'captured': []})
                                else:
                                    break
        moves_to_filter = simple_moves

    # Üçlü tekrar kuralını uygula
    if board_history:
        filtered_moves = []
        for move in moves_to_filter:
            next_state = _simulate_move(board, move)
            # Eğer bu hamle 3. kez aynı pozisyona yol açacaksa, izin verme
            if board_history.count(next_state) < 2:
                filtered_moves.append(move)
        
        # Eğer tüm hamleler tekrar nedeniyle filtrelenirse, oyunu kilitlememek için
        # filtrelenmemiş listeyi döndür (bu durumda beraberlik kuralı devreye girer).
        if not filtered_moves and moves_to_filter:
            return moves_to_filter, is_capture
        return filtered_moves, is_capture

    return moves_to_filter, is_capture
