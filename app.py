# app.py
"""
Flask web sunucusu.
Yapay Zeka Turnuvası için gerekli endpoint'leri içerir.
(BuildError hatası düzeltildi)
"""
from flask import Flask, render_template, jsonify, request
from game.game_manager import GameManager
from game.tournament_manager import TournamentManager

app = Flask(__name__)
game_manager = GameManager()
# Turnuva yöneticisini de başlatıyoruz
tournament_manager = TournamentManager()

@app.route('/')
def home():
    """Ana sayfayı (home.html) render eder, oyun modu seçimi sunar."""
    return render_template('home.html')

@app.route('/pve')
def pve_game():
    """Bilgisayara Karşı oyun modunu başlatır."""
    difficulty = request.args.get('difficulty', 'medium')
    game_manager.reset_game(difficulty=difficulty)
    return render_template('pve.html')

@app.route('/pvp')
def pvp_game():
    """İki Kişilik oyun modunu başlatır."""
    game_manager.reset_game()
    return render_template('pvp.html')

@app.route('/state')
def get_state():
    """Oyunun mevcut durumunu JSON olarak döndürür."""
    return jsonify(game_manager.get_state())

@app.route('/move', methods=['POST'])
def move():
    """PVE modundan gelen oyuncu hamlesini işler ve AI'ın oynamasını tetikler."""
    move_data = request.json
    success = game_manager.make_move(move_data)
    if success and not game_manager.game_over and game_manager.current_player == 'black':
        game_manager.make_ai_move()
    return jsonify(game_manager.get_state())

@app.route('/pvp_move', methods=['POST'])
def pvp_move():
    """PVP modundan gelen oyuncu hamlesini işler (AI olmadan)."""
    move_data = request.json
    game_manager.make_move(move_data)
    return jsonify(game_manager.get_state())

@app.route('/reset', methods=['POST'])
def reset():
    """Oyunu mevcut zorluk seviyesiyle sıfırlar."""
    current_difficulty = game_manager.get_difficulty()
    game_manager.reset_game(difficulty=current_difficulty)
    return jsonify(game_manager.get_state())

# --- BAŞLANGIÇ: Eksik Olan Turnuva Endpoint'leri ---
@app.route('/ai_tournament')
def ai_tournament_page():
    """Turnuva sayfasını render eder."""
    return render_template('ai_tournament.html')

@app.route('/tournament/start', methods=['POST'])
def start_tournament():
    """Turnuvayı başlatır ve ilk durumunu döndürür."""
    tournament_manager.start_tournament()
    return jsonify(tournament_manager.get_state())

@app.route('/tournament/tick', methods=['POST'])
def tournament_tick():
    """Turnuvadaki bir sonraki AI hamlesini oynatır ve durumu döndürür."""
    tournament_manager.play_next_ai_move()
    return jsonify(tournament_manager.get_state())
# --- SON: Eksik Olan Turnuva Endpoint'leri ---

if __name__ == '__main__':
    app.run(debug=True)
