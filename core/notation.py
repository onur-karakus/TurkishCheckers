# core/notation.py
"""
Bu modül, oyun içi hamle verilerini standart dama notasyonuna çevirir.
Örn: [(5, 0), (4, 0)] -> "a3-a4"
"""

def _get_square_notation(r, c):
    """Verilen satır ve sütun indeksini 'a1' gibi bir nota çevirir."""
    # Sütunlar: 0->a, 1->b, ...
    file = chr(ord('a') + c)
    # Satırlar: 7->1, 6->2, ..., 0->8
    rank = str(8 - r)
    return f"{file}{rank}"

def to_dama_notation(move):
    """
    Bir hamle objesini tam notasyon dizesine çevirir.
    Taş almalı hamleler için 'x' kullanır.
    """
    path = move.get('path', [])
    if not path or len(path) < 2:
        return "Geçersiz Hamle"

    # Çoklu taş almalarda (zincirleme hamleler), ara adımlar yerine sadece başlangıç ve bitiş kullanılır.
    # Ancak taş alma 'x' ile belirtilir.
    start_square = _get_square_notation(path[0][0], path[0][1])
    end_square = _get_square_notation(path[-1][0], path[-1][1])
    
    separator = 'x' if move.get('captured') else '-'
    
    return f"{start_square}{separator}{end_square}"
