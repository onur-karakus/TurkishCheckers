# TurkishCheckers/ai/elo.py
import math

# K-faktörü, ELO puanının ne kadar hızlı değişeceğini belirler.
# Daha yüksek değerler daha hızlı ama daha oynak değişimlere neden olur.
K_FACTOR = 32

def calculate_expected_score(player_elo, opponent_elo):
    """
    Bir oyuncunun rakibine karşı beklenen skorunu (kazanma olasılığını) hesaplar.
    ELO farkına dayanır. 400 puanlık bir fark, daha yüksek ELO'lu oyuncunun
    10 kat daha fazla kazanma olasılığına sahip olduğu anlamına gelir.
    """
    return 1 / (1 + math.pow(10, (opponent_elo - player_elo) / 400))

def update_elo(player_elo, opponent_elo, score):
    """
    Maç sonucuna göre oyuncunun yeni ELO puanını hesaplar.
    
    Args:
        player_elo (float): Oyuncunun mevcut ELO'su.
        opponent_elo (float): Rakibin mevcut ELO'su.
        score (float): Maç sonucu (1.0 zafer, 0.5 beraberlik, 0.0 yenilgi).
        
    Returns:
        float: Oyuncunun güncellenmiş yeni ELO puanı.
    """
    expected_score = calculate_expected_score(player_elo, opponent_elo)
    new_elo = player_elo + K_FACTOR * (score - expected_score)
    return new_elo
