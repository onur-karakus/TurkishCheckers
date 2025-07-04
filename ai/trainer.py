# TurkishCheckers/ai/trainer.py
import random
import sys
import os
from tqdm import tqdm

# Proje kök dizinini Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.game_manager import GameManager
from ai.ai_player import (
    AIPlayer, load_pool, save_pool, create_player_pool,
    load_graveyard, save_to_graveyard
)
from ai.elo import update_elo
from core import rules

# --- Genetik Algoritma Parametreleri ---
ELITE_RATE = 0.20        # Havuzun en iyi %20'si elit sayılır ve ebeveyn olur.
RELEGATION_RATE = 0.50   # Havuzun en kötü %50'si her nesilde elenir ve yeniden yaratılır.
MUTATION_RATE = 0.10     # Bir genin (ağırlığın) mutasyona uğrama olasılığı.
MUTATION_AMOUNT = 0.05   # Mutasyonun ne kadar güçlü olacağı (örn: %5'lik değişim).

# --- Yardımcı Fonksiyonlar ---

def select_parents(elite_pool):
    """Elit havuzdan rastgele iki farklı ebeveyn seçer."""
    if len(elite_pool) < 2:
        return elite_pool[0], elite_pool[0]
    return random.sample(elite_pool, 2)

def crossover(parent1, parent2):
    """İki ebeveynin ağırlıklarını birleştirerek yeni bir 'beyin' oluşturur ve birincil ebeveynin DNA'sını döndürür."""
    child_weights = {}
    p1_weights = parent1.weights
    p2_weights = parent2.weights
    
    for key in p1_weights:
        if random.random() < 0.5:
            child_weights[key] = p1_weights[key]
        else:
            child_weights[key] = p2_weights[key]
    
    # Yeni beyni ve kalıtım için kullanılacak DNA'yı döndür
    return child_weights, parent1.dna

def mutate(weights):
    """Bir beyindeki ağırlıkları küçük bir şansla rastgele değiştirir (mutasyon)."""
    mutated_weights = weights.copy()
    for key in mutated_weights:
        if random.random() < MUTATION_RATE:
            change_factor = random.uniform(-MUTATION_AMOUNT, MUTATION_AMOUNT)
            original_value = mutated_weights[key]
            mutated_weights[key] = max(0.01, original_value * (1 + change_factor)) # Değerin 0 olmasını engelle
    return mutated_weights

def are_weights_identical(weights1, weights2, tolerance=1e-9):
    """İki 'beyin' setinin neredeyse birebir aynı olup olmadığını kontrol eder."""
    if weights1.keys() != weights2.keys():
        return False
    for key in weights1:
        if abs(weights1[key] - weights2[key]) > tolerance:
            return False
    return True

def is_duplicate(new_weights, active_pool, graveyard_pool):
    """Yeni bir beynin, yaşayan veya ölü bir beyinle aynı olup olmadığını kontrol eder."""
    for player in active_pool:
        if are_weights_identical(new_weights, player.weights):
            return True
    for player in graveyard_pool:
        if are_weights_identical(new_weights, player.weights):
            return True
    return False

# --- Simülasyon ve Evrim Fonksiyonları ---

def simulate_game(player1, player2):
    """İki AI oyuncusu arasında bir oyun simüle eder."""
    players = {'W': player1, 'B': player2}
    if random.random() < 0.5:
        players = {'W': player2, 'B': player1}

    game = GameManager()
    game.setup_new_game(mode='pve') 
    game.start_game()

    for _ in range(150): # Sonsuz oyunları önlemek için hamle limiti
        if game.game_over:
            break
        
        current_ai_player = players[game.current_player]
        game.ai_weights = current_ai_player.weights
        
        base_time = 0.05
        elo_bonus = max(0, (current_ai_player.elo - 1000) / 1000.0)
        game.ai_time_limit = base_time + elo_bonus

        move_data = game.request_ai_move()
        if not move_data or not move_data.get("move"):
            game.winner = rules.get_opponent(game.current_player)
            game.game_over = True
            break
        start_pos, end_pos = move_data["move"]
        game.play_turn(start_pos, end_pos)

    if game.winner:
        return players.get(game.winner), players.get(rules.get_opponent(game.winner))
    return None, None # Beraberlik

def run_generation(pool, games_per_player, generation_number):
    """Bir nesil boyunca simülasyonu ve evrimi çalıştırır."""
    print(f"Nesil {generation_number} simülasyonu: {len(pool)} oyuncu, her biri ~{games_per_player} oyun...")
    
    num_matches = (len(pool) * games_per_player) // 2
    for _ in tqdm(range(num_matches), desc=f"Nesil {generation_number} Maçları"):
        if len(pool) < 2: continue
        p1, p2 = random.sample(pool, 2)
        original_elo1, original_elo2 = p1.elo, p2.elo
        winner, _ = simulate_game(p1, p2)
        p1_score = 1.0 if winner and winner.id == p1.id else (0.0 if winner else 0.5)
        p1.elo = update_elo(original_elo1, original_elo2, p1_score)
        p2.elo = update_elo(original_elo2, original_elo1, 1.0 - p1_score)

    # --- EVRİM ADIMI ---
    pool.sort(key=lambda p: p.elo, reverse=True)
    
    elite_count = int(len(pool) * ELITE_RATE)
    relegation_start_index = len(pool) - int(len(pool) * RELEGATION_RATE)
    
    elite_pool = pool[:elite_count]
    if not elite_pool: return pool

    relegated_players = pool[relegation_start_index:]
    save_to_graveyard(relegated_players)
    graveyard_pool = load_graveyard()
    
    print(f"Evrim adımı: En alttaki {len(relegated_players)} oyuncu yeniden yaratılıyor...")
    
    for i, player_to_recreate in enumerate(relegated_players):
        new_weights = None
        parent_dna_for_inheritance = None
        attempts = 0
        while attempts < 100: # Sonsuz döngüye karşı önlem
            parent1, parent2 = select_parents(elite_pool)
            candidate_weights, parent_dna = crossover(parent1, parent2)
            mutated_candidate = mutate(candidate_weights)
            
            if not is_duplicate(mutated_candidate, pool, graveyard_pool):
                new_weights = mutated_candidate
                parent_dna_for_inheritance = parent_dna
                break
            attempts += 1
            
        if new_weights:
            player_to_recreate.__init__(
                player_id=player_to_recreate.id,
                generation=generation_number,
                creation_order=i,
                weights=new_weights,
                parent_dna=parent_dna_for_inheritance
            )
            player_to_recreate.elo = 1000
        else:
            print(f"UYARI: {player_to_recreate.name} için 100 denemede benzersiz bir klon üretilemedi. Değiştirilmeden bırakılıyor.")
    return pool

def run_training_session(num_generations=1, games_per_player=10, pool_size=100):
    """Ana evrimsel eğitim fonksiyonu."""
    print("AI Oyuncu Havuzu Yükleniyor veya Oluşturuluyor...")
    pool = load_pool()
    
    start_generation = 0
    if pool:
        start_generation = max(p.generation for p in pool) + 1
        if len(pool) != pool_size:
            print(f"Mevcut havuz boyutu ({len(pool)}) istenen boyuttan ({pool_size}) farklı. Yeni havuz oluşturuluyor.")
            pool = None
    
    if not pool:
        print(f"{pool_size} oyuncudan oluşan yeni bir havuz oluşturuluyor...")
        pool = create_player_pool(pool_size)
        start_generation = 1 # Yeni havuz 1. nesilden başlar

    print(f"{num_generations} nesil boyunca evrimsel simülasyon başlatılıyor...")
    
    for gen in range(start_generation, start_generation + num_generations):
        pool = run_generation(pool, games_per_player, gen)
        save_pool(pool)

    print("\nEvrimsel eğitim tamamlandı.")
    pool.sort(key=lambda p: p.elo, reverse=True)
    print("\n--- Final ELO Sıralaması (Top 10) ---")
    for i, player in enumerate(pool[:10]):
        print(f"{i+1}. {player.name}, ELO: {player.elo:.2f}")

if __name__ == "__main__":
    run_training_session(num_generations=1, games_per_player=10, pool_size=100)
