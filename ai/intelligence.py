import math
import random
import time
from copy import deepcopy
from core.rules import get_possible_moves, make_move, check_game_over
from core.board import Board

# MCTS için sabitler
C_PUCT = 1.41  # Keşif (exploration) sabiti, sqrt(2)'ye yakın bir değer

class Node:
    """
    Monte Carlo Ağacındaki her bir düğümü temsil eder.
    Bir oyun durumunu (state) ve o duruma ilişkin istatistikleri tutar.
    """
    def __init__(self, state: Board, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.move = move  # Bu düğüme gelmeyi sağlayan hamle
        self.wins = 0
        self.visits = 0
        self.is_fully_expanded = self.state.is_game_over()
        self.player_to_move = self.state.get_current_player()

    def __repr__(self):
        return f"Node(move={self.move}, W/V={self.wins}/{self.visits})"

    def select_best_child(self):
        """
        UCB1 (Upper Confidence Bound 1) formülünü kullanarak en iyi çocuğu seçer.
        Bu formül, en çok kazandıran (exploitation) ve en az ziyaret edilen (exploration)
        düğümler arasında bir denge kurar.
        """
        log_parent_visits = math.log(self.visits)

        best_score = -1
        best_child = None

        for child in self.children:
            exploitation_term = child.wins / child.visits
            exploration_term = C_PUCT * math.sqrt(log_parent_visits / child.visits)

            # PUCT (Polynomial Upper Confidence Trees) formülü
            score = exploitation_term + exploration_term

            if score > best_score:
                best_score = score
                best_child = child

        return best_child

    def expand(self):
        """
        Düğümü genişletir. Geçerli tüm hamleler için yeni çocuk düğümler oluşturur.
        """
        if self.is_fully_expanded:
            return None

        legal_moves = self.state.get_possible_moves()

        for move in legal_moves:
            new_board_state = self.state.copy()
            new_board_state.make_move(move['from'], move['to'])

            child_node = Node(new_board_state, parent=self, move=move)
            self.children.append(child_node)

        self.is_fully_expanded = True
        return self.children[0] if self.children else None

    def rollout(self) -> int:
        """
        Simülasyon (veya playout) adımı.
        Bu düğümün durumundan başlayarak oyun sonuna kadar rastgele hamleler oynar.
        Oyunun sonucunu (1: kazanç, -1: kayıp, 0: beraberlik) döndürür.
        """
        current_rollout_state = self.state.copy()

        while not current_rollout_state.is_game_over():
            possible_moves = current_rollout_state.get_possible_moves()
            if not possible_moves:
                break

            # Rastgele bir hamle seç
            action = random.choice(possible_moves)
            current_rollout_state.make_move(action['from'], action['to'])

        winner = current_rollout_state.get_winner()
        if winner is None:
            return 0
        # Sonucu, bu düğümdeki oyuncunun perspektifinden döndür
        return 1 if winner == self.player_to_move else -1

    def backpropagate(self, result: int):
        """
        Simülasyon sonucunu ağaçta yukarı doğru günceller.
        """
        node = self
        while node is not None:
            node.visits += 1
            # Sonuç, her üst seviyedeki oyuncunun perspektifine göre ayarlanır.
            # Eğer mevcut düğümün oyuncusu, sonucu getiren oyuncu ile aynı ise, bu bir kazançtır.
            if node.player_to_move != self.player_to_move:
                 node.wins -= result # Rakip için -1, bizim için +1 demek
            else:
                 node.wins += result

            node = node.parent

class MCTS:
    """
    Monte Carlo Tree Search algoritmasını yöneten ana sınıf.
    """
    def __init__(self, board: Board, time_limit_seconds=None, iteration_limit=None):
        if time_limit_seconds is None and iteration_limit is None:
            raise ValueError("Either time_limit_seconds or iteration_limit must be set.")

        self.root = Node(state=board)
        self.time_limit = time.time() + time_limit_seconds if time_limit_seconds else float('inf')
        self.iteration_limit = iteration_limit if iteration_limit is not None else float('inf')

    def run_search(self):
        """
        Belirlenen süre veya iterasyon limiti dolana kadar MCTS algoritmasını çalıştırır.
        """
        iterations = 0
        while time.time() < self.time_limit and iterations < self.iteration_limit:

            # 1. Selection: Kök'ten başlayarak umut vaat eden bir yaprak düğüme in.
            leaf = self._select(self.root)

            # 2. Expansion: Eğer oyun bitmediyse bu yaprağı genişlet.
            if not leaf.is_fully_expanded:
                leaf = leaf.expand()

            # 3. Simulation (Rollout): Genişletilen düğümden oyun sonuna kadar simülasyon yap.
            if leaf:
                simulation_result = leaf.rollout()

                # 4. Backpropagation: Simülasyon sonucunu ağaçta yukarı doğru yay.
                leaf.backpropagate(simulation_result)

            iterations += 1

        print(f"MCTS search completed after {iterations} iterations.")

    def _select(self, node: Node) -> Node:
        """
        Selection adımını gerçekleştirir.
        """
        current_node = node
        while current_node.is_fully_expanded and not current_node.state.is_game_over():
            current_node = current_node.select_best_child()
        return current_node

    def get_best_move(self):
        """
        Arama bittikten sonra en iyi hamleyi (en çok ziyaret edilen) ve değerlendirmeyi döndürür.
        """
        if not self.root.children:
            return None, 0.0

        # En çok ziyaret edilen (en güvenilir) hamleyi seç
        best_child = max(self.root.children, key=lambda c: c.visits)

        # Değerlendirme skoru: Kazanma oranı (-1 ile 1 arasında)
        # Eğer hiç ziyaret edilmemişse, nötr bir skor (0) döndür
        evaluation = (best_child.wins / best_child.visits) if best_child.visits > 0 else 0.0

        return best_child.move, evaluation


def find_best_move(board: Board, player_color: str, difficulty: str):
    """
    Belirtilen zorluk seviyesine göre MCTS kullanarak en iyi hamleyi bulur.

    Args:
        board: Mevcut oyun tahtası.
        player_color: Hamle yapacak olan yapay zekanın rengi ('white' veya 'black').
        difficulty: 'Easy', 'Medium', veya 'Hard'.

    Returns:
        (best_move, evaluation)
        best_move: Sözlük formatında en iyi hamle.
        evaluation: Tahtanın değerlendirme skoru (-1.0 ile 1.0 arası).
    """

    # Zorluk seviyesine göre iterasyon sayısını belirle
    difficulty_map = {
        'Easy': 100,
        'Medium': 500,
        'Hard': 2000
    }
    iterations = difficulty_map.get(difficulty, 500)

    # MCTS'i başlat ve çalıştır
    mcts = MCTS(board=board, iteration_limit=iterations)
    mcts.run_search()

    # En iyi hamleyi ve skoru al
    best_move, evaluation = mcts.get_best_move()

    # Eğer AI için hiç hamle bulunamazsa (oyun bitmiş olabilir)
    if best_move is None:
        return None, 0.0

    print(f"AI ({player_color}, {difficulty}) found best move: {best_move} with eval: {evaluation:.2f}")

    return best_move, evaluation

