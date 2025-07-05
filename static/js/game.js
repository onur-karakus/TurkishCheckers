// static/js/game.js
document.addEventListener('DOMContentLoaded', () => {
    const boardElement = document.getElementById('board');
    const newGameBtn = document.getElementById('new-game-btn');
    const modalNewGameBtn = document.getElementById('modal-new-game');
    
    let boardState = [], currentPlayer = '', validMoves = [], selectedPiece = null;
    const PIECES = { W_MAN: 1, B_MAN: 2, W_KING: 3, B_KING: 4 };

    function getPieceColor(p) { return (p === 1 || p === 3) ? 'white' : 'black'; }
    function isKing(p) { return p === 3 || p === 4; }

    // --- BAŞLANGIÇ: Arayüz Güncelleme Yardımcı Fonksiyonu ---
    function updateUI(state) {
        if (!state) return;
        boardState = state.board;
        currentPlayer = state.currentPlayer;
        validMoves = state.validMoves;

        drawBoard();
        updateInfoPanel(state);
        updateEvaluation(state.evaluation);
        updateCapturedPieces(state.capturedByWhite, state.capturedByBlack);
        updateNotation(state.move_history);

        if (state.gameOver) {
            handleGameOver(state);
        }
    }
    // --- SON: Arayüz Güncelleme Yardımcı Fonksiyonu ---

    async function updateGameState() {
        try {
            const response = await fetch('/state');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const state = await response.json();
            updateUI(state);
        } catch (error) {
            console.error('Oyun durumu alınamadı:', error);
            const gameStatusElement = document.getElementById('game-status');
            if(gameStatusElement) gameStatusElement.textContent = "Sunucuyla bağlantı kurulamadı.";
        }
    }

    function drawBoard() {
        if (!boardElement) return;
        boardElement.innerHTML = '';
        const mandatoryStartPositions = validMoves.map(move => `${move.path[0][0]},${move.path[0][1]}`);
        for (let r = 0; r < 8; r++) {
            for (let c = 0; c < 8; c++) {
                const square = document.createElement('div');
                square.classList.add('square', (r + c) % 2 === 0 ? 'light' : 'dark');
                square.dataset.r = r; square.dataset.c = c;
                const pieceType = boardState[r][c];
                if (pieceType !== 0) {
                    const piece = document.createElement('div');
                    piece.classList.add('piece', getPieceColor(pieceType));
                    if (isKing(pieceType)) piece.classList.add('king');
                    if (getPieceColor(pieceType) === currentPlayer && mandatoryStartPositions.includes(`${r},${c}`)) { piece.classList.add('mandatory'); }
                    square.appendChild(piece);
                }
                boardElement.appendChild(square);
            }
        }
        highlightValidMoves();
    }

    function highlightValidMoves() {
        if (!boardElement) return;
        document.querySelectorAll('.selected, .valid-move').forEach(el => el.classList.remove('selected', 'valid-move'));
        if (!selectedPiece) return;
        const pieceElement = boardElement.querySelector(`[data-r='${selectedPiece.r}'][data-c='${selectedPiece.c}'] .piece`);
        if (pieceElement) pieceElement.classList.add('selected');
        const possibleEndPositions = validMoves.filter(move => move.path[0][0] === selectedPiece.r && move.path[0][1] === selectedPiece.c).map(move => move.path[move.path.length - 1]);
        possibleEndPositions.forEach(([r, c]) => {
            const square = boardElement.querySelector(`[data-r='${r}'][data-c='${c}']`);
            if (square) square.classList.add('valid-move');
        });
    }

    function updateInfoPanel(state) {
        const turnInfoElement = document.getElementById('turn-info'); const gameStatusElement = document.getElementById('game-status');
        if (!turnInfoElement || !gameStatusElement) return;
        turnInfoElement.textContent = `Sıra: ${state.currentPlayer === 'white' ? 'Beyaz' : 'Siyah'}`;
        gameStatusElement.textContent = (validMoves.length > 0 && validMoves[0].captured.length > 0 && state.currentPlayer === 'white') ? 'Zorunlu hamle var!' : '';
    }

    function updateCapturedPieces(whiteCaptures, blackCaptures) {
        const whiteCapturedElement = document.querySelector('#white-captured .captured-pieces'); const blackCapturedElement = document.querySelector('#black-captured .captured-pieces');
        if (!whiteCapturedElement || !blackCapturedElement) return;
        whiteCapturedElement.innerHTML = '';
        for (let i = 0; i < whiteCaptures; i++) { const captured = document.createElement('div'); captured.className = 'captured-piece piece black'; whiteCapturedElement.appendChild(captured); }
        blackCapturedElement.innerHTML = '';
        for (let i = 0; i < blackCaptures; i++) { const captured = document.createElement('div'); captured.className = 'captured-piece piece white'; blackCapturedElement.appendChild(captured); }
    }

    function updateEvaluation(percentage) {
        const evalBarWhite = document.getElementById('eval-bar-white'); const evalBarBlack = document.getElementById('eval-bar-black'); const evalText = document.getElementById('eval-text');
        if (!evalBarWhite || !evalBarBlack || !evalText) return;
        const whitePercentage = Math.round(percentage); const blackPercentage = 100 - whitePercentage;
        evalBarWhite.style.width = `${whitePercentage}%`; evalBarBlack.style.width = `${blackPercentage}%`; evalText.textContent = `${whitePercentage}%`;
    }

    function updateNotation(history) {
        const notationList = document.getElementById('notation-list');
        if (!notationList || !history) return;
        notationList.innerHTML = '';
        history.forEach(move => {
            const li = document.createElement('li');
            li.textContent = move;
            notationList.appendChild(li);
        });
        notationList.scrollTop = notationList.scrollHeight;
    }

    async function handleSquareClick(e) {
        if (currentPlayer !== 'white') return;
        const square = e.target.closest('.square');
        if (!square) return;
        const r = parseInt(square.dataset.r); const c = parseInt(square.dataset.c);
        if (selectedPiece) {
            const move = validMoves.find(m => m.path[0][0] === selectedPiece.r && m.path[0][1] === selectedPiece.c && m.path[m.path.length - 1][0] === r && m.path[m.path.length - 1][1] === c);
            if (move) { await sendMove(move); selectedPiece = null; return; }
        }
        selectedPiece = null;
        const pieceType = boardState[r][c];
        if (pieceType !== 0 && getPieceColor(pieceType) === currentPlayer) {
            const isSelectable = validMoves.some(m => m.path[0][0] === r && m.path[0][1] === c);
            if (isSelectable) { selectedPiece = { r, c, type: pieceType }; }
        }
        drawBoard();
    }

    // --- BAŞLANGIÇ: Düzeltilmiş Hamle Gönderme Mantığı ---
    async function sendMove(move) {
        try {
            const response = await fetch('/move', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(move), });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const state = await response.json(); // Yanıtı doğrudan kullan
            updateUI(state); // Arayüzü yeni durumla güncelle
        } catch (error) { console.error('Hamle gönderilemedi:', error); }
    }
    // --- SON: Düzeltilmiş Hamle Gönderme Mantığı ---
    
    function handleGameOver(state) {
        let message = "Oyun Bitti!";
        if (state.winner === 'draw') { message = "Gayyım! Oyun berabere."; } else { const winnerName = state.winner === 'white' ? 'Beyaz' : 'Siyah'; message = `${winnerName} kazandı!`; }
        showModal(message);
    }

    async function resetGame() {
        await fetch('/reset', { method: 'POST' });
        selectedPiece = null;
        const modal = document.getElementById('modal');
        if(modal) modal.classList.add('hidden');
        await updateGameState();
    }

    function showModal(message) {
        const modal = document.getElementById('modal'); const modalMessage = document.getElementById('modal-message');
        if (!modal || !modalMessage) return;
        modalMessage.textContent = message; modal.classList.remove('hidden');
    }

    if (boardElement) { boardElement.addEventListener('click', handleSquareClick); }
    if (newGameBtn) { newGameBtn.addEventListener('click', resetGame); }
    if (modalNewGameBtn) { modalNewGameBtn.addEventListener('click', resetGame); }

    updateGameState();
});
