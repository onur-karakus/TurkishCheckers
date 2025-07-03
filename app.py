# TurkishCheckers/app.py
import os
import io
import unittest
import random
from flask import Flask, render_template, request, redirect, url_for, jsonify

from game.game_manager import GameManager
from game.session_handler import (
    get_game_from_session,
    save_game_to_session,
    create_new_game_in_session,
    clear_game_session
)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default-insecure-secret-key-for-dev")

@app.route('/')
def home():
    clear_game_session()
    return render_template('home.html')

@app.route('/play-vs-friend', methods=['GET'])
def play_vs_friend():
    game_manager = get_game_from_session()
    if game_manager is None or game_manager.mode != 'pvp':
        game_manager = create_new_game_in_session(mode='pvp')
    return render_template('pvp.html', game_state=game_manager.to_dict())

@app.route('/play-vs-computer', methods=['GET'])
def play_vs_computer():
    game_manager = get_game_from_session()
    if game_manager is None or game_manager.mode != 'pve':
        game_manager = create_new_game_in_session(mode='pve')
    return render_template('pve.html', game_state=game_manager.to_dict())

# --- API Endpoints ---

@app.route('/api/start_game', methods=['POST'])
def start_game():
    data = request.get_json()
    mode = data.get('mode', 'pve')
    
    if mode == 'pve':
        difficulty = int(data.get('difficulty', 50))
        player_color = data.get('player_color', 'W')
        if player_color == 'Random':
            player_color = random.choice(['W', 'B'])
        
        game_manager = create_new_game_in_session(
            mode='pve', 
            difficulty=difficulty, 
            player_color=player_color
        )
    else: # pvp
        time_control = data.get('time_control', '600_0')
        game_manager = create_new_game_in_session(mode='pvp', time_control=time_control)
    
    game_manager.start_game()
    save_game_to_session(game_manager)
    return jsonify(game_manager.to_dict())

@app.route('/api/resign', methods=['POST'])
def resign():
    game_manager = get_game_from_session()
    if not game_manager or not game_manager.is_active:
        return jsonify({"error": "Sonlandırılacak aktif bir oyun yok."}), 400
    
    game_manager.resign()
    save_game_to_session(game_manager)
    return jsonify(game_manager.to_dict())


@app.route('/api/play', methods=['POST'])
def play():
    """
    DÜZELTME: Bu endpoint artık anında yanıt verir. Gereksiz analiz çağrısı kaldırıldı.
    """
    game_manager = get_game_from_session()
    if not game_manager or not game_manager.is_active or game_manager.game_over:
        return jsonify({"error": "Oyun aktif değil veya bitmiş."}), 400
    
    data = request.get_json()
    start_pos, end_pos = (data['start']['row'], data['start']['col']), (data['end']['row'], data['end']['col'])
    
    if game_manager.time_control_active and 'time_left' in data:
        game_manager.update_time(data['time_left'])
        
    move_result = game_manager.play_turn(start_pos, end_pos)
    if not move_result["success"]:
        return jsonify({"error": move_result["message"], "game": game_manager.to_dict()}), 400
    
    # Hamle sonrası oyun durumunu hemen döndür.
    response_data = game_manager.to_dict()
    response_data.update({
        "move_path": move_result["path"],
        "captured_pieces_this_turn": game_manager.captured_pieces_this_turn,
        "move_type": move_result["type"]
    })
    
    save_game_to_session(game_manager)
    return jsonify(response_data)

@app.route('/api/ai_move', methods=['POST'])
def ai_move():
    game_manager = get_game_from_session()
    if not game_manager or not game_manager.is_active or game_manager.game_over or game_manager.current_player != game_manager.ai_player_color:
        return jsonify({"error": "Yapay zeka hamlesi için uygun durum değil."}), 400
    
    # AI burada düşünür.
    move_data = game_manager.request_ai_move()
    if not move_data or not move_data.get("move"):
        game_manager.check_game_over()
        save_game_to_session(game_manager)
        return jsonify({"error": "AI hamle bulamadı.", "game": game_manager.to_dict()}), 400
    
    # AI'ın bulduğu hamleyi uygula.
    start_pos, end_pos = move_data["move"]
    move_result = game_manager.play_turn(start_pos, end_pos)
    if not move_result["success"]:
        return jsonify({"error": "AI geçersiz bir hamle üretti.", "game": game_manager.to_dict()}), 500
    
    # AI hamlesinden sonraki pozisyon için analiz yap.
    game_dict = game_manager.to_dict()
    if not game_manager.game_over:
        analysis_data = game_manager.get_engine_analysis()
        game_dict['analysis'] = analysis_data
        
    game_dict.update({
        "move_path": move_result["path"],
        "captured_pieces_this_turn": game_manager.captured_pieces_this_turn,
        "move_type": move_result["type"]
    })
    
    save_game_to_session(game_manager)
    return jsonify(game_dict)

@app.route('/api/get_analysis', methods=['GET'])
def get_analysis():
    game_manager = get_game_from_session()
    if not game_manager or not game_manager.is_active or game_manager.game_over:
        return jsonify({"error": "Analiz için oyun bulunamadı veya bitti."}), 400
    analysis_data = game_manager.get_engine_analysis()
    return jsonify(analysis_data)

@app.route('/api/valid_moves/<int:r>/<int:c>', methods=['GET'])
def get_valid_moves(r, c):
    game_manager = get_game_from_session()
    if not game_manager: return jsonify({"error": "Oyun aktif değil."}), 400
    valid_moves = game_manager.get_valid_moves_for_piece(r, c)
    return jsonify({"moves": valid_moves})

@app.route('/api/timeout', methods=['POST'])
def handle_timeout():
    game_manager = get_game_from_session()
    if not game_manager or not game_manager.is_active or game_manager.game_over:
        return jsonify({"error": "Oyun aktif değil veya bitmiş."}), 400
    game_manager.handle_timeout()
    save_game_to_session(game_manager)
    return jsonify(game_manager.to_dict())

@app.route('/test')
def run_tests():
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='tests')
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    output = stream.getvalue()
    summary = f"Toplam Test: {result.testsRun}, Hatalı: {len(result.errors)}, Başarısız: {len(result.failures)}"
    return f"<h1>Test Sonuçları</h1><p>{summary}</p><pre>{output}</pre>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
