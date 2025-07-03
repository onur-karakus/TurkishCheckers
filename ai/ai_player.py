# TurkishCheckers/ai/ai_player.py
import random
import json
import os
import string

# --- Sabitler ve Dosya Yolları ---
AI_POOL_PATH = os.path.join(os.path.dirname(__file__), 'ai_pool.json')
AI_GRAVEYARD_PATH = os.path.join(os.path.dirname(__file__), 'ai_graveyard.json')

class AIPlayer:
    """
    Bir yapay zeka oyuncusunu temsil eder. Bu sürüm, nesil tabanlı kimlik,
    genetik DNA ve mezarlık sistemi gibi gelişmiş özellikleri içerir.
    """
    def __init__(self, player_id, generation, creation_order, elo=1000, weights=None, parent_dna=None):
        """
        Yeni bir AI oyuncusu oluşturur.

        Args:
            player_id (int): Oyuncunun benzersiz ID'si (sabit kalır).
            generation (int): Oyuncunun oluşturulduğu nesil.
            creation_order (int): Nesil içindeki oluşturulma sırası.
            elo (float): Başlangıç ELO puanı.
            weights (dict, optional): Oyuncunun beyni. Yoksa, rastgele oluşturulur.
            parent_dna (str, optional): Kalıtım için kullanılacak 3 harfli ebeveyn DNA'sı.
        """
        self.id = player_id
        self.elo = elo
        
        # --- YENİ KİMLİK SİSTEMİ ---
        self.generation = generation
        self.creation_order = creation_order
        
        # DNA'yı oluştur: Son harf ebeveynden kalıtsal, ilk ikisi rastgele.
        if parent_dna and len(parent_dna) == 3:
            inherited_char = parent_dna[-1]
            new_chars = ''.join(random.choice(string.ascii_uppercase) for _ in range(2))
            self.dna = new_chars + inherited_char
        else:
            # Ebeveyn yoksa (ilk nesil) veya DNA geçersizse, tamamen rastgele oluştur.
            self.dna = ''.join(random.choice(string.ascii_uppercase) for _ in range(3))

        # İsmi yeni formata göre oluştur: Örn: 001001ABC
        self.name = f"{self.generation:03d}{self.creation_order:03d}{self.dna}"

        if weights:
            self.weights = weights
        else:
            self.weights = self._generate_random_weights()

    def _generate_random_weights(self):
        """Yeni bir AI için rastgele stratejik ağırlıklar oluşturur."""
        return {
            "piece_value": random.uniform(8.0, 12.0),
            "dama_value": random.uniform(25.0, 35.0),
            "advancement_bonus": random.uniform(0.1, 0.6),
            "center_control_bonus": random.uniform(0.1, 0.6),
            "defensive_bonus": random.uniform(0.05, 0.4)
        }

    def to_dict(self):
        """Oyuncu nesnesini JSON'a yazmak için sözlüğe dönüştürür."""
        return {
            "id": self.id, 
            "name": self.name, 
            "elo": self.elo, 
            "weights": self.weights,
            "generation": self.generation,
            "creation_order": self.creation_order,
            "dna": self.dna
        }

    @classmethod
    def from_dict(cls, data):
        """Sözlükten bir oyuncu nesnesi oluşturur."""
        # Eski oyuncu verileriyle uyumluluk için .get() kullanılır.
        creation_order = data.get('creation_order', data.get('id', 0))
        
        # Eğer eski bir 'name' formatı varsa, onu ayrıştırarak nesil ve DNA'yı çıkarmaya çalış
        generation = data.get('generation', 0)
        dna = data.get('dna')
        if not dna and len(data.get('name', '')) > 6:
            try:
                name_str = data['name']
                generation = int(name_str[0:3])
                # creation_order = int(name_str[3:6]) # ID'yi korumak daha iyi
                dna = name_str[6:9]
            except (ValueError, IndexError):
                pass # Ayrıştırma başarısız olursa varsayılanlar kullanılır

        return cls(
            player_id=data['id'], 
            elo=data.get('elo', 1000), 
            weights=data['weights'],
            generation=generation,
            creation_order=creation_order,
            parent_dna=dna # Mevcut DNA, bir sonraki nesil için ebeveyn DNA'sı olur
        )

# --- Havuz ve Mezarlık Yönetim Fonksiyonları ---

def create_player_pool(size=100):
    """Belirtilen boyutta, 0. nesil bir AI oyuncu havuzu oluşturur."""
    return [AIPlayer(player_id=i, generation=0, creation_order=i) for i in range(size)]

def save_pool(pool, filename=AI_POOL_PATH):
    """Oyuncu havuzunu bir JSON dosyasına kaydeder."""
    pool.sort(key=lambda p: p.elo, reverse=True)
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([player.to_dict() for player in pool], f, indent=4)
        print(f"{len(pool)} oyuncu başarıyla '{filename}' dosyasına kaydedildi.")
    except IOError as e:
        print(f"HATA: '{filename}' dosyasına yazılamadı. Hata: {e}")

def load_pool(filename=AI_POOL_PATH):
    """Bir JSON dosyasından oyuncu havuzunu yükler."""
    if not os.path.exists(filename):
        print(f"Uyarı: '{filename}' bulunamadı. Yeni bir havuz oluşturulacak.")
        return None
        
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            pool = [AIPlayer.from_dict(p_data) for p_data in data]
            pool.sort(key=lambda p: p.elo, reverse=True)
            print(f"{len(pool)} oyuncu '{filename}' dosyasından yüklendi.")
            return pool
    except (json.JSONDecodeError, IOError, KeyError) as e:
        print(f"HATA: '{filename}' dosyası okunurken bir hata oluştu: {e}")
        return None

def load_graveyard(filename=AI_GRAVEYARD_PATH):
    """Daha önce elenmiş AI'ların listesini yükler."""
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [AIPlayer.from_dict(p_data) for p_data in data]
    except (json.JSONDecodeError, IOError):
        print(f"Uyarı: Mezarlık dosyası ('{filename}') okunamadı veya boş.")
        return []

def save_to_graveyard(relegated_players, filename=AI_GRAVEYARD_PATH):
    """Elenen oyuncuları mezarlık dosyasına ekler."""
    graveyard = load_graveyard(filename)
    existing_ids = {p.id for p in graveyard}
    
    newly_relegated = [p for p in relegated_players if p.id not in existing_ids]
    if not newly_relegated:
        return

    graveyard.extend(newly_relegated)
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([player.to_dict() for player in graveyard], f, indent=4)
        print(f"{len(newly_relegated)} yeni oyuncu mezarlığa eklendi.")
    except IOError as e:
        print(f"HATA: Mezarlık dosyasına yazılamadı: {e}")

def get_default_ai_weights():
    """Oyun için varsayılan bir AI 'beyni' döndürür."""
    pool = load_pool()
    if pool:
        return pool[0].weights
    
    print("Varsayılan AI havuzu bulunamadı, standart ağırlıklar kullanılıyor.")
    return AIPlayer(player_id=0, generation=0, creation_order=0).weights
