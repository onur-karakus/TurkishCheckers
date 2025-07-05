import uuid
from core.board import Board
from core.rules import check_game_over
from core.notation import get_move_notation

class GameManager:
    """
    Aktif oyun oturumlarını yöneten sınıf.
    Her oyunun tahta durumunu, oyuncu sıralamasını ve hamle geçmişini tutar.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameManager, cls).__new__(cls)
            cls._instance.games = {}
        return cls._instance

    def create_game(self, player_white, player_black, game_mode='pve'):
        """Yeni bir oyun oturumu oluşturur."""
        game_id = str(uuid.uuid4())
        board = Board()
        self.games[game_id] = {
            'board': board,
            'player_white': player_white,
            'player_black': player_black,
            'current_player': 'white',
            'game_mode': game_mode,
            'move_history': [], # Hamle geçmişi listesi eklendi
            'status': 'ongoing',
            'winner': None
        }
        return game_id

    def get_game_state(self, game_id):
        """Bir oyunun mevcut durumunu döndürür."""
        game = self.games.get(game_id)
        if not game:
            return None

        board_state = game['board'].get_board_state()

        return {
            'game_id': game_id,
            'board_state': board_state,
            'current_player': game['board'].get_current_player(),
            'game_mode': game['game_mode'],
            'move_history': game['move_history'], # Hamle geçmişini state'e ekle
            'status': game['status'],
            'winner': game['winner']
        }

    def make_move(self, game_id, from_sq, to_sq, player_color):
        """
        Bir oyuncunun hamlesini işler.
        Hamle geçerliyse tahtayı günceller, hamleyi kaydeder ve oyun durumunu kontrol eder.
        """
        game = self.games.get(game_id)
        if not game or game['status'] != 'ongoing':
            return {'success': False, 'message': 'Oyun bulunamadı veya bitti.'}

        board = game['board']
        if board.get_current_player() != player_color:
            return {'success': False, 'message': 'Sıra sizde değil.'}

        # Hamle notasyonunu al
        notation = get_move_notation(board, from_sq, to_sq)

        # Hamleyi yap
        move_result = board.make_move(from_sq, to_sq)
        if not move_result['success']:
            return {'success': False, 'message': move_result['message']}

        # Hamle başarılıysa, geçmişe ekle
        turn_number = len(game['move_history']) // 2 + 1
        if player_color == 'white':
            game['move_history'].append(f"{turn_number}. {notation}")
        else:
            # Beyazın hamlesini bul ve sonuna ekle
            if len(game['move_history']) % 2 != 0:
                 game['move_history'][-1] += f" {notation}"
            else: # Eğer beyaz hamle yapmadıysa (hata durumu)
                 game['move_history'].append(f"... {notation}")


        # Oyunun bitip bitmediğini kontrol et
        winner = board.get_winner()
        if winner:
            game['status'] = 'finished'
            game['winner'] = winner

        return {
            'success': True,
            'board_state': board.get_board_state(),
            'current_player': board.get_current_player(),
            'move_history': game['move_history'],
            'winner': game['winner']
        }

    def end_game(self, game_id):
        """Bir oyunu sonlandırır ve hafızadan siler."""
        if game_id in self.games:
            del self.games[game_id]
            return True
        return False
