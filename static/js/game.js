document.addEventListener('DOMContentLoaded', () => {
    const boardElement = document.getElementById('game-board');
    let selectedPiece = null;
    let possibleMoves = [];

    // UI Elemanları
    const currentTurnElement = document.getElementById('current-turn');
    const gameOverMessageElement = document.getElementById('game-over-message');
    const winnerElement = document.getElementById('winner');
    const moveListElement = document.getElementById('move-list');
    const evalBarWhite = document.getElementById('eval-bar-white');
    const evalBarBlack = document.getElementById('eval-bar-black');
    const evalScoreElement = document.getElementById('eval-score');


    const createBoard = (boardState) => {
        boardElement.innerHTML = '';
        for (let r = 0; r < 8; r++) {
            for (let c = 0; c < 8; c++) {
                const square = document.createElement('div');
                square.classList.add('square');
                square.classList.add((r + c) % 2 === 0 ? 'light' : 'dark');
                square.dataset.row = r;
                square.dataset.col = c;

                const pieceData = boardState[r][c];
                if (pieceData) {
                    const piece = document.createElement('div');
                    piece.classList.add('piece', pieceData.color);
                    if (pieceData.is_king) {
                        piece.classList.add('king');
                    }
                    square.appendChild(piece);
                }
                boardElement.appendChild(square);
            }
        }
        addSquareListeners();
    };

    const handleSquareClick = async (event) => {
        const square = event.currentTarget;
        const row = parseInt(square.dataset.row);
        const col = parseInt(square.dataset.col);

        if (selectedPiece) {
            const move = possibleMoves.find(m => m.to[0] === row && m.to[1] === col);
            if (move) {
                // Hamleyi yap
                const from_sq = selectedPiece;
                const to_sq = [row, col];
                const response = await makePlayerMove(from_sq, to_sq);
                if (response.success) {
                    updateBoardAndGameState(response);
                    // Sıra AI'daysa AI hamlesi iste
                    if (response.current_player !== PLAYER_COLOR && !response.winner) {
                        setTimeout(requestAiMove, 500);
                    }
                }
            }
            // Seçimi temizle
            clearSelection();
        } else {
            // Bir taşa tıklandıysa ve sıra oyuncudaysa
            if (square.hasChildNodes()) {
                const piece = square.firstChild;
                const pieceColor = piece.classList.contains('white') ? 'white' : 'black';
                if (pieceColor === PLAYER_COLOR) {
                    const response = await getPossibleMovesForPiece(row, col);
                    if (response.moves) {
                        selectPiece([row, col], response.moves);
                    }
                }
            }
        }
    };

    const selectPiece = (coords, moves) => {
        clearSelection();
        selectedPiece = coords;
        possibleMoves = moves;
        // Seçili taşı ve olası hamleleri vurgula
        document.querySelector(`[data-row='${coords[0]}'][data-col='${coords[1]}']`).classList.add('selected');
        moves.forEach(move => {
            document.querySelector(`[data-row='${move.to[0]}'][data-col='${move.to[1]}']`).classList.add('possible-move');
        });
    };

    const clearSelection = () => {
        selectedPiece = null;
        possibleMoves = [];
        document.querySelectorAll('.selected').forEach(el => el.classList.remove('selected'));
        document.querySelectorAll('.possible-move').forEach(el => el.classList.remove('possible-move'));
    };

    const updateBoardAndGameState = (gameState) => {
        createBoard(gameState.board_state);
        updateCurrentTurn(gameState.current_player);
        updateMoveHistory(gameState.move_history);
        if (gameState.evaluation !== undefined) {
            updateEvaluationBar(gameState.evaluation);
        }
        if (gameState.winner) {
            showGameOver(gameState.winner);
        }
    };

    const updateCurrentTurn = (player) => {
        currentTurnElement.textContent = player === 'white' ? 'Beyaz' : 'Siyah';
    };

    const showGameOver = (winner) => {
        winnerElement.textContent = winner === 'white' ? 'Beyaz' : 'Siyah';
        gameOverMessageElement.classList.remove('hidden');
    };

    // YENİ: Hamle Geçmişini Güncelle
    const updateMoveHistory = (history) => {
        moveListElement.innerHTML = '';
        if (history) {
            history.forEach(move => {
                const li = document.createElement('li');
                li.textContent = move;
                moveListElement.appendChild(li);
            });
            // Otomatik olarak en alta kaydır
            moveListElement.scrollTop = moveListElement.scrollHeight;
        }
    };

    // YENİ: Değerlendirme Çubuğunu Güncelle
    const updateEvaluationBar = (evaluation) => {
        // evaluation -1 (siyah üstün) ile +1 (beyaz üstün) arasında bir değerdir.
        const score = parseFloat(evaluation);

        // Değeri %50 - %50'lik bir orana çevir
        const white_percentage = (score + 1) / 2 * 100;
        const black_percentage = 100 - white_percentage;

        evalBarWhite.style.width = `${white_percentage}%`;
        evalBarBlack.style.width = `${black_percentage}%`;

        // Skoru göster (genellikle satranç motorları gibi +1.25 formatında)
        // MCTS'den gelen -1..1 aralığını daha anlaşılır bir skora çevirebiliriz.
        const display_score = score * 5; // Örneğin -5 ile +5 arası bir skalaya oturtalım.
        evalScoreElement.textContent = `${display_score >= 0 ? '+' : ''}${display_score.toFixed(2)}`;
    };


    const addSquareListeners = () => {
        document.querySelectorAll('.square').forEach(square => {
            square.addEventListener('click', handleSquareClick);
        });
    };

    const initializeGame = async () => {
        const initialState = await getGameState(GAME_ID);
        if (initialState) {
            updateBoardAndGameState(initialState);
            if (initialState.current_player !== PLAYER_COLOR && !initialState.winner) {
                 setTimeout(requestAiMove, 500);
            }
        }
    };

    const requestAiMove = async () => {
        console.log("Requesting AI move...");
        const response = await makeAiMove(GAME_ID, AI_DIFFICULTY);
        if (response.success) {
            updateBoardAndGameState(response);
        } else {
            console.error("AI move failed:", response.message);
        }
    };

    initializeGame();
});

