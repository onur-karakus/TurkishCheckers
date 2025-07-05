# Dama Pozisyon Notasyonu (PDN) benzeri basit bir gösterim
# Tahtadaki koordinatları (row, col) cebirsel notasyona (a1, b2 vb.) çevirir.

def to_algebraic(row, col):
    """(0,0) -> 'a8', (7,7) -> 'h1' gibi dönüşüm yapar."""
    if not (0 <= row <= 7 and 0 <= col <= 7):
        return ""
    file = chr(ord('a') + col)
    rank = str(8 - row)
    return f"{file}{rank}"

def get_move_notation(board, from_sq, to_sq):
    """
    Verilen başlangıç ve bitiş karelerine göre hamle notasyonunu oluşturur.
    Örn: "c3-d4" veya "c3xd5"
    """
    from_alg = to_algebraic(from_sq[0], from_sq[1])
    to_alg = to_algebraic(to_sq[0], to_sq[1])

    # Hamlenin taş alıp almadığını kontrol et
    # Basit bir yaklaşımla, aradaki kare sayısına bakabiliriz
    is_capture = abs(from_sq[0] - to_sq[0]) > 1 or abs(from_sq[1] - to_sq[1]) > 1
    separator = 'x' if is_capture else '-'

    return f"{from_alg}{separator}{to_alg}"

