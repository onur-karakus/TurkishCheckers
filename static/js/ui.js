// static/js/ui.js

/**
 * DÜZELTME: Bu sürüm, eksik olan bindPanelEvents fonksiyonunu ekleyerek
 * "is not a function" hatasını giderir ve arayüzün doğru çalışmasını sağlar.
 */
export default class UIManager {
    constructor() {
        this.elements = {
            boardContainer: document.getElementById('board-container'),
            board: document.getElementById('board'),
            messageArea: document.querySelector('.message'),
            newGameSettings: document.getElementById('new-game-settings'),
            activeGameControls: document.getElementById('active-game-controls'),
            analysisPanel: document.querySelector('.analysis-container'),
            arrowContainer: document.getElementById('arrow-container'),
            playerInfoTop: document.getElementById('player-info-top'),
            playerInfoBottom: document.getElementById('player-info-bottom'),
            notationListContainer: document.getElementById('notation-list-container'),
            difficultySlider: document.getElementById('difficulty-slider'),
            difficultyValue: document.getElementById('difficulty-value'),
            evalBarWhite: document.getElementById('eval-bar-white'),
            evalScore: document.getElementById('evaluation-score'),
            engineLines: document.getElementById('engine-lines'),
        };
        this.selectedSquare = null;
        this.squareCenterCache = {};
    }

    /**
     * Kontrol panelindeki olay dinleyicilerini bağlar.
     */
    bindPanelEvents() {
        // Zorluk çubuğu için olay dinleyicisi
        this.elements.difficultySlider?.addEventListener('input', () => {
            if (this.elements.difficultyValue) {
                this.elements.difficultyValue.textContent = this.elements.difficultySlider.value;
            }
        });

        // Renk seçimi butonları için olay dinleyicisi
        const colorOptions = document.querySelectorAll('.color-option');
        colorOptions.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                colorOptions.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
            });
        });
    }

    calculateSquarePositions() {
        this.squareCenterCache = {};
        const boardRect = this.elements.board?.getBoundingClientRect();
        if (!boardRect || boardRect.width === 0) return;
        for (let r = 0; r < 8; r++) {
            for (let c = 0; c < 8; c++) {
                const square = this.getSquare(r, c);
                if (square) {
                    const squareRect = square.getBoundingClientRect();
                    this.squareCenterCache[`${r}-${c}`] = {
                        x: (squareRect.left - boardRect.left) + (squareRect.width / 2),
                        y: (squareRect.top - boardRect.top) + (squareRect.height / 2)
                    };
                }
            }
        }
    }

    drawBoard(boardState) {
        return new Promise(resolve => {
            if (!this.elements.board) return resolve();
            this.elements.board.innerHTML = '';
            if (!boardState) return resolve();
            boardState.forEach((row, r) => {
                row.forEach((piece, c) => {
                    const square = document.createElement('div');
                    square.className = `square ${(r + c) % 2 !== 0 ? 'dark' : 'light'}`;
                    square.dataset.row = r;
                    square.dataset.col = c;
                    if (piece !== ' ') {
                        const pieceDiv = document.createElement('div');
                        const isWhite = piece.toUpperCase() === 'W';
                        pieceDiv.className = `piece piece-${isWhite ? 'white' : 'black'}`;
                        if (piece.toLowerCase() === piece) pieceDiv.innerHTML = `<span class="dama-crown">★</span>`;
                        square.appendChild(pieceDiv);
                    }
                    this.elements.board.appendChild(square);
                });
            });
            requestAnimationFrame(() => {
                this.calculateSquarePositions();
                resolve();
            });
        });
    }

    async animateMove(moveData) {
        this.disableBoard(true);
        const { move_path: path } = moveData;
        const DURATION = 250;
        const startPos = path[0];
        const startSquare = this.getSquare(startPos[0], startPos[1]);
        const originalPiece = startSquare?.querySelector('.piece');
        if (!originalPiece || Object.keys(this.squareCenterCache).length === 0) {
            await this.drawBoard(moveData.board);
            this.disableBoard(false);
            return;
        }
        const movingPiece = originalPiece.cloneNode(true);
        this.elements.board.appendChild(movingPiece);
        movingPiece.classList.add('animating-piece');
        originalPiece.style.visibility = 'hidden';
        const pieceSize = originalPiece.offsetWidth;
        for (let i = 0; i < path.length - 1; i++) {
            const currentPos = path[i];
            const nextPos = path[i + 1];
            const startCoords = this.squareCenterCache[`${currentPos[0]}-${currentPos[1]}`];
            const endCoords = this.squareCenterCache[`${nextPos[0]}-${nextPos[1]}`];
            movingPiece.style.left = `${startCoords.x - pieceSize / 2}px`;
            movingPiece.style.top = `${startCoords.y - pieceSize / 2}px`;
            movingPiece.style.transform = 'none';
            await new Promise(resolve => {
                requestAnimationFrame(() => {
                    movingPiece.style.transition = `transform ${DURATION}ms ease-in-out`;
                    const deltaX = endCoords.x - startCoords.x;
                    const deltaY = endCoords.y - startCoords.y;
                    movingPiece.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
                    movingPiece.addEventListener('transitionend', resolve, { once: true });
                });
            });
        }
        if (this.elements.board.contains(movingPiece)) {
            this.elements.board.removeChild(movingPiece);
        }
        await this.drawBoard(moveData.board);
        this.disableBoard(false);
    }
    
    updateUIState(gameState) {
        this.elements.newGameSettings.classList.toggle('hidden', gameState.is_active);
        this.elements.activeGameControls.classList.toggle('hidden', !gameState.is_active);
        this.elements.analysisPanel.classList.toggle('hidden', !gameState.is_active);
        this.disableBoard(!gameState.is_active || gameState.game_over);
        if (!gameState.is_active) {
            this.clearArrow();
        }
    }
    
    updatePlayerIndicators(gameState) {
        const { current_player, mode, time_white, time_black, game_over, difficulty, player_color } = gameState;
        const topBox = this.elements.playerInfoTop;
        const bottomBox = this.elements.playerInfoBottom;
        if (!topBox || !bottomBox) return;
        const topNameEl = topBox.querySelector('.player-name');
        const bottomNameEl = bottomBox.querySelector('.player-name');
        const topClockEl = topBox.querySelector('.player-clock');
        const bottomClockEl = bottomBox.querySelector('.player-clock');
        if (mode === 'pve') {
            const humanIsWhite = player_color === 'W';
            bottomNameEl.textContent = humanIsWhite ? "Siz (Beyaz)" : "Siz (Siyah)";
            topNameEl.textContent = `Bilgisayar (${difficulty || 50})`;
            this.updateClock(bottomClockEl, humanIsWhite ? time_white : time_black);
            this.updateClock(topClockEl, humanIsWhite ? time_black : time_white);
        } else {
            bottomNameEl.textContent = "Beyaz";
            topNameEl.textContent = "Siyah";
            this.updateClock(bottomClockEl, time_white);
            this.updateClock(topClockEl, time_black);
        }
        topBox.classList.remove('active');
        bottomBox.classList.remove('active');
        if (!game_over && gameState.is_active) {
            if (current_player === 'W') {
                bottomBox.classList.add('active');
            } else {
                topBox.classList.add('active');
            }
        }
    }

    updateClock(clockEl, seconds) {
        if (!clockEl) return;
        if (seconds === null || seconds === undefined) {
            clockEl.style.display = 'none';
            return;
        }
        clockEl.style.display = 'block';
        if (seconds < 0) seconds = 0;
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        clockEl.textContent = `${String(mins).padStart(1, '0')}:${String(secs).padStart(2, '0')}`;
    }

    updateNotationPanel(notations) {
        const container = this.elements.notationListContainer;
        if (!container) return;
        container.innerHTML = '';
        if (!notations || notations.length === 0) return;
        const ol = document.createElement('ol');
        for (let i = 0; i < notations.length; i += 2) {
            const li = document.createElement('li');
            li.innerHTML = `<span class="move-white">${notations[i] || ''}</span><span class="move-black">${notations[i + 1] || ''}</span>`;
            ol.appendChild(li);
        }
        container.appendChild(ol);
        container.scrollTop = container.scrollHeight;
    }

    updateAnalysisPanel(analysis, currentPlayer) {
        if (!this.elements.analysisPanel || !analysis || analysis.win_prob === undefined) {
            if (this.elements.engineLines) this.elements.engineLines.innerHTML = '<li>Analiz bekleniyor...</li>';
            this.clearArrow();
            return;
        }
        
        const winProb = analysis.win_prob;
        const whiteWinProb = (currentPlayer === 'W') ? winProb : (100.0 - winProb);
        
        if (this.elements.evalBarWhite) {
            this.elements.evalBarWhite.style.width = `${whiteWinProb}%`;
        }
        
        if (this.elements.evalScore) {
            this.elements.evalScore.textContent = `${whiteWinProb.toFixed(1)}%`;
        }

        if (this.elements.engineLines) {
            this.elements.engineLines.innerHTML = '';
            if (analysis.top_moves && analysis.top_moves.length > 0) {
                analysis.top_moves.forEach(move => {
                    const li = document.createElement('li');
                    const moveWinProb = move.win_prob;
                    const moveWhiteWinProb = (currentPlayer === 'W') ? moveWinProb : (100.0 - moveWinProb);
                    
                    li.innerHTML = `<strong>${move.variation}</strong> <span class="score">(${moveWhiteWinProb.toFixed(1)}%)</span>`;
                    this.elements.engineLines.appendChild(li);
                });
                const bestMovePath = analysis.top_moves[0].move_path;
                this.drawArrow(bestMovePath);
            } else {
                this.elements.engineLines.innerHTML = '<li>Hamle bulunamadı.</li>';
                this.clearArrow();
            }
        }
    }

    drawArrow(path) {
        if (!this.elements.arrowContainer || !path || path.length < 2) return;
        this.clearArrow();
        
        const svgNS = "http://www.w3.org/2000/svg";
        const defs = document.createElementNS(svgNS, 'defs');
        const marker = document.createElementNS(svgNS, 'marker');
        marker.setAttribute('id', 'arrowhead');
        marker.setAttribute('viewBox', '0 0 10 10');
        marker.setAttribute('refX', '10');
        marker.setAttribute('refY', '5');
        marker.setAttribute('markerWidth', '6');
        marker.setAttribute('markerHeight', '6');
        marker.setAttribute('orient', 'auto-start-reverse');
        const arrowPath = document.createElementNS(svgNS, 'path');
        arrowPath.setAttribute('d', 'M 0 0 L 10 5 L 0 10 z');
        arrowPath.style.fill = 'rgba(25, 135, 84, 0.8)';
        marker.appendChild(arrowPath);
        defs.appendChild(marker);
        this.elements.arrowContainer.appendChild(defs);

        for (let i = 0; i < path.length - 1; i++) {
            const start = path[i];
            const end = path[i+1];

            const startCoords = this.squareCenterCache[`${start[0]}-${start[1]}`];
            const endCoords = this.squareCenterCache[`${end[0]}-${end[1]}`];
            if (!startCoords || !endCoords) continue;

            const line = document.createElementNS(svgNS, 'line');
            line.setAttribute('x1', startCoords.x);
            line.setAttribute('y1', startCoords.y);
            line.setAttribute('x2', endCoords.x);
            line.setAttribute('y2', endCoords.y);
            line.setAttribute('marker-end', 'url(#arrowhead)');
            this.elements.arrowContainer.appendChild(line);
        }
    }

    clearArrow() { if (this.elements.arrowContainer) this.elements.arrowContainer.innerHTML = ''; }
    disableBoard(isDisabled) { this.elements.boardContainer?.classList.toggle('board-disabled', isDisabled); }
    updateMessage(msg, isThinking = false) { if (this.elements.messageArea) { this.elements.messageArea.innerText = msg || ''; this.elements.messageArea.classList.toggle('thinking', isThinking); } }
    clearSelection() { if (this.selectedSquare) { this.selectedSquare.classList.remove('selected'); this.selectedSquare = null; } document.querySelectorAll('.valid-move').forEach(vm => vm.classList.remove('valid-move')); }
    selectSquare(square) { this.clearSelection(); this.selectedSquare = square; square.classList.add('selected'); }
    highlightValidMoves(moves) { moves.forEach(([r, c]) => { this.getSquare(r, c)?.classList.add('valid-move'); }); }
    getSquare(r, c) { return this.elements.board?.querySelector(`.square[data-row='${r}'][data-col='${c}']`); }
}
