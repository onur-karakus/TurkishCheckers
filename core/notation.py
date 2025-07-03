# TurkishCheckers/core/notation.py

def to_algebraic(r, c):
    """
    Tahta koordinatlarını (satır, sütun) cebirsel notasyona (ör: a1, h8) çevirir.
    
    Args:
        r (int): Satır indeksi (0-7).
        c (int): Sütun indeksi (0-7).
        
    Returns:
        str: Cebirsel notasyon.
    """
    # Sütun 'a' ile 'h' arasına, satır '8' ile '1' arasına eşlenir.
    file = chr(ord('a') + c)
    rank = str(8 - r)
    return f"{file}{rank}"

def from_algebraic(notation_str):
    """
    Cebirsel notasyonu (ör: a1) tahta koordinatlarına (satır, sütun) çevirir.
    
    Args:
        notation_str (str): Cebirsel notasyon.
        
    Returns:
        tuple[int, int] | None: (satır, sütun) veya geçersizse None.
    """
    if not isinstance(notation_str, str) or len(notation_str) != 2:
        return None
    
    file = notation_str[0].lower()
    rank = notation_str[1]
    
    if not ('a' <= file <= 'h' and '1' <= rank <= '8'):
        return None
        
    c = ord(file) - ord('a')
    r = 8 - int(rank)
    
    return r, c

def path_to_notation(path, move_type):
    """
    Bir hamle yolunu (path) tam cebirsel notasyona dönüştürür.
    
    Args:
        path (list[tuple]): Hamlenin izlediği koordinat yolu.
        move_type (str): 'capture' veya 'normal'.
        
    Returns:
        str: Tam notasyon (ör: "a3-b3" veya "c2xh4").
    """
    if not path or len(path) < 2:
        return ""
        
    start_r, start_c = path[0]
    end_r, end_c = path[-1]
    
    separator = "x" if move_type == 'capture' else "-"
    
    start_notation = to_algebraic(start_r, start_c)
    end_notation = to_algebraic(end_r, end_c)
    
    return f"{start_notation}{separator}{end_notation}"

