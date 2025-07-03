# TurkishCheckers/core/board.py

# --- Sabitler ---
WHITE_PIECE = 'W'
BLACK_PIECE = 'B'
WHITE_DAMA = 'w'
BLACK_DAMA = 'b'
EMPTY_SQUARE = ' '

BOARD_SIZE = 8

def setup_new_board():
    """
    Türk Daması için başlangıç dizilimine sahip 8x8 bir tahta oluşturur.
    
    Returns:
        list[list[str]]: Oyun tahtasını temsil eden 2D liste.
    """
    board = [[EMPTY_SQUARE for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    
    # Beyaz taşları yerleştir (alt iki sıra)
    for row in [5, 6]:
        for col in range(BOARD_SIZE):
            board[row][col] = WHITE_PIECE
            
    # Siyah taşları yerleştir (üst iki sıra)
    for row in [1, 2]:
        for col in range(BOARD_SIZE):
            board[row][col] = BLACK_PIECE
            
    return board

def count_pieces(board_state):
    """
    Tahtadaki beyaz ve siyah taşların sayısını (dama dahil) sayar.
    
    Args:
        board_state (list[list[str]]): Mevcut tahta durumu.
        
    Returns:
        tuple[int, int]: (beyaz_tas_sayisi, siyah_tas_sayisi)
    """
    w_pieces = sum(row.count(WHITE_PIECE) + row.count(WHITE_DAMA) for row in board_state)
    b_pieces = sum(row.count(BLACK_PIECE) + row.count(BLACK_DAMA) for row in board_state)
    return w_pieces, b_pieces

def is_within_bounds(r, c):
    """Verilen koordinatların tahta sınırları içinde olup olmadığını kontrol eder."""
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE
