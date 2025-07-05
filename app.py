from flask import Flask, render_template, request, jsonify, session
from game.game_manager import GameManager
from game.session_handler import SessionHandler
from ai.ai_player import AIPlayer

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_checkers'

game_manager = GameManager()
session_handler = SessionHandler()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/options')
def options():
    return render_template('options.html')

@app.route('/pve', methods=['GET', 'POST'])
def pve():
    if request.method == 'POST':
        player_color = request.form.get('color', 'white')
        difficulty = request.form.get('difficulty', 'Medium')

        session_id = session_handler.get_session_id()
        player_white = session_id if player_color == 'white' else 'AI'
        player_black = 'AI' if player_color == 'white' else session_id

        game_id = game_manager.create_game(player_white, player_black, game_mode='pve')
        session['game_id'] = game_id
        session['player_color'] = player_color
        session['difficulty'] = difficulty

        return render_template('pve.html', game_id=game_id, player_color=player_color, difficulty=difficulty)

    return render_template('options.html')

@app.route('/pvp', methods=['GET', 'POST'])
def pvp():
    if request.method == 'POST':
        # PvP oyun oluşturma mantığı buraya gelecek
        pass
    return render_template('pvp.html')


@app.route('/ai_tournament')
def ai_tournament_page():
    return render_template('ai_tournament.html')

@app.route('/game_state/<game_id>')
def game_state(game_id):
    state = game_manager.get_game_state(game_id)
    if state:
        return jsonify(state)
    return jsonify({'error': 'Game not found'}), 404

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    game_id = data.get('game_id')
    from_sq = tuple(data.get('from_sq'))
    to_sq = tuple(data.get('to_sq'))
    player_color = data.get('player_color')

    if not game_id or from_sq is None or to_sq is None or player_color is None:
        return jsonify({'success': False, 'message': 'Eksik bilgi.'}), 400

    result = game_manager.make_move(game_id, from_sq, to_sq, player_color)
    return jsonify(result)


@app.route('/ai_move', methods=['POST'])
def ai_move():
    data = request.json
    game_id = data.get('game_id')
    difficulty = data.get('difficulty', 'Medium')

    game = game_manager.games.get(game_id)
    if not game:
        return jsonify({'success': False, 'message': 'Oyun bulunamadı.'}), 404

    board = game['board']
    ai_color = board.get_current_player()

    # AI oyuncusundan hamle ve değerlendirme al
    ai_player = AIPlayer(ai_color, difficulty)
    move, evaluation = ai_player.get_move(board)

    if move is None:
        return jsonify({'success': False, 'message': 'AI hamle bulamadı.'})

    # Hamleyi oyun yöneticisi üzerinden yap
    result = game_manager.make_move(game_id, move['from'], move['to'], ai_color)

    # Sonuca AI değerlendirmesini ekle
    result['evaluation'] = evaluation

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

