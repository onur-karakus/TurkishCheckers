# TurkishCheckers/game/session_handler.py
from flask import session
from .game_manager import GameManager
from ai.ai_player import get_default_ai_weights

def get_game_from_session() -> GameManager | None:
    """
    Flask oturumundan (session) oyun durumunu alır ve bir GameManager nesnesi oluşturur.
    Oturumda oyun durumu yoksa None döndürür.
    """
    game_state_dict = session.get('game_state')
    if not game_state_dict:
        return None
    
    return GameManager.from_dict(game_state_dict)

def save_game_to_session(game_manager: GameManager):
    """
    Verilen GameManager nesnesinin durumunu Flask oturumuna kaydeder.
    """
    session['game_state'] = game_manager.to_dict()
    session.modified = True

def create_new_game_in_session(mode='pve', difficulty=50, time_control='unlimited', player_color='W') -> GameManager:
    """
    Yeni bir GameManager nesnesi oluşturur, ayarlarını yapar, oturuma kaydeder
    ve oluşturulan nesneyi döndürür.
    """
    game_manager = GameManager()
    game_manager.setup_new_game(
        mode=mode,
        player_color=player_color,
        difficulty=difficulty,
        time_control=time_control
    )
    # Varsayılan AI ağırlıklarını ata
    game_manager.ai_weights = get_default_ai_weights()
    
    save_game_to_session(game_manager)
    return game_manager

def clear_game_session():
    """Oyunla ilgili oturum verilerini temizler."""
    session.pop('game_state', None)

