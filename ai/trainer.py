# ai/trainer.py
import random
import sys
import os
from tqdm import tqdm

# Proje kök dizinini Python yoluna ekle (betiğin tek başına çalışabilmesi için)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game_logic import Game
from ai.ai_player import AIPlayer, load_pool, save_pool, create_player_pool
from ai.elo import update_elo

# --- Genetik Algoritma Parametreleri ---
ELITE_RATE = 0.20      # Ebeveyn olarak seçilecek en iyi oyuncu oranı
RELEGATION_RATE = 0.50 # Beyni (ağırlıkları) değiştirilecek en kötü oyuncu oranı
MUTATION_RATE = 0.05   # Bir genin (ağırlığın) mutasyona uğrama olasılığı
MUTATION_AMOUNT = 0.1  # Mutasyonun ne kadar büyük olacağı (yüzde olarak)

def select_parents(elite_pool):
    """Elit havuzdan rastgele iki farklı ebeveyn seçer."""
    if len(elite_pool) < 2:
        return elite_pool[0], elite_pool[0]
    return random.sample(elite_pool, 2)

def crossover(parent1, parent2):
    """İki ebeveynin ağırlıklarını (genlerini) birleştirerek yeni bir 'beyin' (weights) oluşturur."""
    child_weights = {}
    p1_weights = parent1.weights
    p2_weights = parent2.weights
    
    for key in p1_weights:
        if random.random() < 0.5:
            child_weights[key] = p1_weights[key]
        else:
            child_weights[key] = p2_weights[key]
    return child_weights

def mutate(weights):
    """Bir beyindeki ağırlıkları (genleri) küçük bir şansla rastgele değiştirir (mutasyon)."""
    mutated_weights = weights.copy()
    for key in mutated_weights:
        if random.random() < MUTATION_RATE:
            change_factor = random.uniform(-MUTATION_AMOUNT, MUTATION_AMOUNT)
            original_value = mutated_weights[key]
            mutated_weights[key] = max(0, original_value * (1 + change_factor))
    return mutated_weights

def run_generation(pool, games_per_player=5):
    """Bir nesil boyunca simülasyonu çalıştırır."""
    if not pool:
        print("Havuz boş, nesil çalıştırılamıyor.")
        return []

    print(f"Nesil simülasyonu: {len(pool)} oyuncu, her biri ~{games_per_player} oyun...")
    
    num_matches = (len(pool) * games_per_player) // 2
    for _ in tqdm(range(num_matches), desc="Maçlar Oynanıyor"):
        if len(pool) < 2: continue
        p1, p2 = random.sample(pool, 2)
        
        original_elo1, original_elo2 = p1.elo, p2.elo
        
        winner, _ = simulate_game(p1, p2)
        
        p1_score = 0.5
        if winner:
            p1_score = 1.0 if winner.id == p1.id else 0.0
            
        p1.elo = update_elo(original_elo1, original_elo2, p1_score)
        p2.elo = update_elo(original_elo2, original_elo1, 1.0 - p1_score)

    pool.sort(key=lambda p: p.elo, reverse=True)
    
    elite_count = int(len(pool) * ELITE_RATE)
    relegation_start_index = len(pool) - int(len(pool) * RELEGATION_RATE)
    
    elite_pool = pool[:elite_count]
    if not elite_pool: return pool # Evrim için yeterli elit yoksa devam etme

    relegated_pool = pool[relegation_start_index:]
    
    print(f"Evrim adımı: En alttaki {len(relegated_pool)} oyuncunun beyni, en üstteki {len(elite_pool)} oyuncudan gelen yeni beyinlerle değiştiriliyor...")
    
    for player_to_relegate in relegated_pool:
        parent1, parent2 = select_parents(elite_pool)
        new_weights = crossover(parent1, parent2)
        new_weights = mutate(new_weights)
        player_to_relegate.weights = new_weights
        
    return pool

def simulate_game(player1, player2):
    """İki AI oyuncusu arasında bir oyun simüle eder."""
    players = { 'W': player1, 'B': player2 }
    if random.random() < 0.5:
        players = { 'W': player2, 'B': player1 }

    game = Game(mode='eve')
    
    for _ in range(150):
        if game.game_over: break
        
        current_ai_player = players[game.current_player]
        move = game.get_computer_move(ai_weights=current_ai_player.weights, search_depth=2)

        if not move or not move[0]:
            winner_color = game.get_opponent(game.current_player)
            game.game_over = True
            game.winner = winner_color
            break

        start_pos, end_pos = move
        game.play_turn(start_pos, end_pos)

    if game.winner:
        return players[game.winner], players.get(game.get_opponent(game.winner))
    return None, None

def run_training_session(num_generations=10, games_per_player=10):
    """Ana evrimsel eğitim fonksiyonu. Flask uygulamasından çağrılabilir."""
    print("AI Oyuncu Havuzu Yükleniyor veya Oluşturuluyor...")
    pool = load_pool("ai/ai_pool.json")
    if not pool:
        print("Mevcut havuz bulunamadı. 100 oyuncudan oluşan yeni bir havuz oluşturuluyor...")
        pool = create_player_pool(100)
    
    print(f"{num_generations} nesil boyunca evrimsel simülasyon başlatılıyor...")
    
    for gen in range(num_generations):
        print(f"\n--- NESİL {gen + 1}/{num_generations} ---")
        pool = run_generation(pool, games_per_player)
        save_pool(pool, "ai/ai_pool.json") 

    print("\nEvrimsel eğitim tamamlandı.")
    
    pool.sort(key=lambda p: p.elo, reverse=True)
    
    print("\n--- Final ELO Sıralaması (Top 10) ---")
    for i, player in enumerate(pool[:10]):
        print(f"{i+1}. {player.name}, ELO: {player.elo:.2f}")

if __name__ == "__main__":
    # Bu betik doğrudan çalıştırıldığında varsayılan bir eğitim oturumu başlatır.
    run_training_session(num_generations=5, games_per_player=5)
