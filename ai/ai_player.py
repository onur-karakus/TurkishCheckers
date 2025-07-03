# TurkishCheckers/ai/ai_player.py
import random
import json
import os

class AIPlayer:
    """
    Bir yapay zeka oyuncusunu temsil eder. Oyuncunun ID'si, adı, ELO puanı ve
    en önemlisi, karar verme mekanizmasında kullandığı 'weights' (ağırlıklar)
    yani "beynini" içerir.
    """
    def __init__(self, player_id, elo=1000, weights=None, name=None):
        self.id = player_id
        self.name = name if name else f"AI-{(player_id + 1):03d}"
        self.elo = elo
        
        if weights:
            self.weights = weights
        else:
            # Yeni bir oyuncu için varsayılan ve rastgele ağırlıklar oluştur
            self.weights = self._generate_random_weights()

    def _generate_random_weights(self):
        """Yeni bir AI için rastgele stratejik ağırlıklar oluşturur."""
        return {
            # Temel Değerler: Bir taşın ve bir damanın ne kadar değerli olduğu
            "piece_value": random.uniform(8.0, 12.0),
            "dama_value": random.uniform(25.0, 35.0),
            
            # Stratejik Bonuslar: Oyuncunun neye öncelik vereceğini belirler
            "advancement_bonus": random.uniform(0.1, 0.6), # Taşları ileri sürme eğilimi
            "center_control_bonus": random.uniform(0.1, 0.6), # Tahtanın merkezini kontrol etme eğilimi
            "defensive_bonus": random.uniform(0.05, 0.4) # Kendi sahasındaki taşları koruma eğilimi
        }

    def to_dict(self):
        """Oyuncu nesnesini JSON'a yazmak için sözlüğe dönüştürür."""
        return {"id": self.id, "name": self.name, "elo": self.elo, "weights": self.weights}

    @classmethod
    def from_dict(cls, data):
        """Sözlükten bir oyuncu nesnesi oluşturur."""
        return cls(
            player_id=data['id'], 
            elo=data.get('elo', 1000), 
            weights=data['weights'],
            name=data.get('name')
        )

# --- Havuz Yönetim Fonksiyonları ---

AI_POOL_PATH = os.path.join(os.path.dirname(__file__), 'ai_pool.json')

def create_player_pool(size=100):
    """Belirtilen boyutta bir AI oyuncu havuzu oluşturur."""
    return [AIPlayer(player_id=i) for i in range(size)]

def save_pool(pool, filename=AI_POOL_PATH):
    """Oyuncu havuzunu bir JSON dosyasına kaydeder."""
    # Kaydetmeden önce ELO'ya göre sırala
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
    except json.JSONDecodeError:
        print(f"HATA: '{filename}' dosyası bozuk veya geçersiz JSON formatında.")
        return None
    except (IOError, KeyError) as e:
        print(f"HATA: '{filename}' dosyası okunurken bir hata oluştu: {e}")
        return None

def get_default_ai_weights():
    """
    Oyun için varsayılan bir AI "beyni" döndürür.
    Havuzdan en yüksek ELO'lu oyuncuyu alır veya bir tane oluşturur.
    """
    pool = load_pool()
    if pool:
        return pool[0].weights
    
    # Havuz yoksa veya boşsa, standart bir varsayılan oluştur
    print("Varsayılan AI havuzu bulunamadı, standart ağırlıklar kullanılıyor.")
    return {
        "piece_value": 10.0, 
        "dama_value": 27.5,
        "advancement_bonus": 0.3, 
        "center_control_bonus": 0.2,
        "defensive_bonus": 0.15
    }

