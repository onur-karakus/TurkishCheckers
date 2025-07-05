# ai_tournament.py
"""
Bu betik, farklı zorluk seviyelerindeki yapay zeka oyuncuları arasında
bir turnuva düzenler ve sonuçları ekrana yazdırır.
LCZero'dan ilham alan yeni AIPlayer sınıfını kullanır.
"""
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai.ai_player import AIPlayer
from core import rules

def play_game(white_player, black_player):
    """
    İki yapay zeka oyuncusu arasında bir oyun simüle eder ve sonucu döndürür.
    """
    board = [[0] * 8 for _ in range(8)]
    for i in range(8):
        board[1][i], board[2][i] = 2, 2
        board[5][i], board[6][i] = 1, 1

    current_player_color = 'white'
    move_count = 0
    max_moves = 150

    while move_count < max_moves:
        possible_moves, is_capture = rules.get_all_valid_moves(board, current_player_color)
        
        white_pieces = sum(row.count(1) + row.count(3) for row in board)
        black_pieces = sum(row.count(2) + row.count(4) for row in board)
        if white_pieces == 0: return 'black'
        if black_pieces == 0: return 'white'
        if white_pieces == 1 and black_pieces == 1: return 'draw'
        if not possible_moves:
            return 'black' if current_player_color == 'white' else 'white'

        active_player = white_player if current_player_color == 'white' else black_player
        
        # Hamle alırken, AI'ın döndürdüğü hamlenin tam objesini bulmamız gerekiyor
        # (alınan taşlar bilgisi için)
        ai_move_path = active_player.get_move(board)
        if not ai_move_path:
             return 'black' if current_player_color == 'white' else 'white'
        
        # AI'dan gelen path'e uyan tam hamle objesini bul
        move = None
        for m in possible_moves:
            if m['path'] == ai_move_path['path']:
                move = m
                break
        
        if not move: # AI geçersiz bir path döndürdüyse
            print(f"HATA: {current_player_color} oyuncusu geçersiz bir hamle yolu döndürdü. Rastgele hamle yapılıyor.")
            move = random.choice(possible_moves)

        start_pos, end_pos = move['path'][0], move['path'][-1]
        piece = board[start_pos[0]][start_pos[1]]
        board[start_pos[0]][start_pos[1]] = 0
        
        promoted_piece = piece
        if current_player_color == 'white' and end_pos[0] == 0: promoted_piece = 3
        elif current_player_color == 'black' and end_pos[0] == 7: promoted_piece = 4
        board[end_pos[0]][end_pos[1]] = promoted_piece

        for r, c in move.get('captured', []):
            board[r][c] = 0

        current_player_color = 'black' if current_player_color == 'white' else 'white'
        move_count += 1
        print(f"Hamle {move_count}: {current_player_color} oynayacak.")


    return 'draw'

def main():
    """Turnuvayı başlatır ve sonuçları gösterir."""
    print("Gelişmiş Yapay Zeka Turnuvası Başlatılıyor...")
    print("Bu işlem, her hamle için yapılan derin hesaplamalar nedeniyle uzun sürebilir.")
    print("-" * 40)

    players = {
        "Kolay": AIPlayer('white', time_limit_seconds=2),
        "Orta": AIPlayer('white', time_limit_seconds=5),
        "Zor": AIPlayer('white', time_limit_seconds=10)
    }

    player_names = list(players.keys())
    scores = {name: {'wins': 0, 'draws': 0, 'losses': 0, 'points': 0.0} for name in player_names}
    
    match_ups = []
    for i in range(len(player_names)):
        for j in range(i + 1, len(player_names)):
            match_ups.append((player_names[i], player_names[j]))

    total_matches = len(match_ups) * 2
    current_match = 0

    for p1_name, p2_name in match_ups:
        p1 = players[p1_name]
        p2 = players[p2_name]

        # Maç 1
        current_match += 1
        print(f"\n--- Maç {current_match}/{total_matches}: {p1_name} (Beyaz) vs {p2_name} (Siyah) ---")
        p1.player_color = 'white'
        p2.player_color = 'black'
        winner = play_game(p1, p2)
        print(f"--> Sonuç: {winner if winner != 'draw' else 'Berabere'}")
        if winner == 'white':
            scores[p1_name]['wins'] += 1; scores[p1_name]['points'] += 1.0; scores[p2_name]['losses'] += 1
        elif winner == 'black':
            scores[p2_name]['wins'] += 1; scores[p2_name]['points'] += 1.0; scores[p1_name]['losses'] += 1
        else:
            scores[p1_name]['draws'] += 1; scores[p1_name]['points'] += 0.5; scores[p2_name]['draws'] += 1; scores[p2_name]['points'] += 0.5

        # Maç 2
        current_match += 1
        print(f"\n--- Maç {current_match}/{total_matches}: {p2_name} (Beyaz) vs {p1_name} (Siyah) ---")
        p2.player_color = 'white'
        p1.player_color = 'black'
        winner = play_game(p2, p1)
        print(f"--> Sonuç: {winner if winner != 'draw' else 'Berabere'}")
        if winner == 'white':
            scores[p2_name]['wins'] += 1; scores[p2_name]['points'] += 1.0; scores[p1_name]['losses'] += 1
        elif winner == 'black':
            scores[p1_name]['wins'] += 1; scores[p1_name]['points'] += 1.0; scores[p2_name]['losses'] += 1
        else:
            scores[p1_name]['draws'] += 1; scores[p1_name]['points'] += 0.5; scores[p2_name]['draws'] += 1; scores[p2_name]['points'] += 0.5
        
    print("\n" + "=" * 60)
    print("--- TURNUVA SONUÇLARI ---")
    sorted_scores = sorted(scores.items(), key=lambda item: item[1]['points'], reverse=True)
    print(f"{'Seviye':<10} | {'Galibiyet':<10} | {'Beraberlik':<12} | {'Mağlubiyet':<12} | {'Puan':<5}")
    print("-" * 60)
    for name, result in sorted_scores:
        print(f"{name:<10} | {result['wins']:<10} | {result['draws']:<12} | {result['losses']:<12} | {result['points']!s:<5}")
    print("=" * 60)

if __name__ == "__main__":
    main()
