// static/js/ai_tournament.js
document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('start-tournament-btn');
    const boardElement = document.getElementById('board');
    const matchInfoElement = document.getElementById('match-info');
    const scoreboardBody = document.querySelector('#scoreboard tbody');
    const scheduleBody = document.querySelector('#schedule tbody');

    const PIECES = { W_MAN: 1, B_MAN: 2, W_KING: 3, B_KING: 4 };
    function getPieceColor(p) { return (p === 1 || p === 3) ? 'white' : 'black'; }
    function isKing(p) { return p === 3 || p === 4; }

    function drawBoard(board) {
        if (!boardElement || !board) return;
        boardElement.innerHTML = '';
        for (let r = 0; r < 8; r++) {
            for (let c = 0; c < 8; c++) {
                const square = document.createElement('div');
                square.classList.add('square', (r + c) % 2 === 0 ? 'light' : 'dark');
                const pieceType = board[r][c];
                if (pieceType !== 0) {
                    const piece = document.createElement('div');
                    piece.classList.add('piece', getPieceColor(pieceType));
                    if (isKing(pieceType)) piece.classList.add('king');
                    square.appendChild(piece);
                }
                boardElement.appendChild(square);
            }
        }
    }
    
    function updateEvaluation(percentage) {
        const evalBarWhite = document.getElementById('eval-bar-white');
        const evalBarBlack = document.getElementById('eval-bar-black');
        const evalText = document.getElementById('eval-text');
        if (!evalBarWhite || !evalBarBlack || !evalText) return;

        // --- BAŞLANGIÇ: NaN Hatası Düzeltmesi ---
        // Gelen 'percentage' değerinin geçerli bir sayı olup olmadığını kontrol et.
        let validPercentage = percentage;
        if (typeof validPercentage !== 'number' || isNaN(validPercentage)) {
            // Eğer geçersizse, varsayılan olarak 50 ata ve konsola uyarı yaz.
            console.warn(`Geçersiz değerlendirme değeri alındı: ${percentage}. Varsayılan 50 olarak ayarlandı.`);
            validPercentage = 50;
        }
        // --- SON: NaN Hatası Düzeltmesi ---

        const whitePercentage = Math.round(validPercentage);
        const blackPercentage = 100 - whitePercentage;
        evalBarWhite.style.width = `${whitePercentage}%`;
        evalBarBlack.style.width = `${blackPercentage}%`;
        evalText.textContent = `${whitePercentage}%`;
    }

    function updateUI(state) {
        if (!state) return;
        drawBoard(state.board);
        updateEvaluation(state.evaluation);
        
        if (state.isRunning && state.currentMatchIndex < state.schedule.length) {
            const match = state.schedule[state.currentMatchIndex];
            let turnText = `Sıra: ${state.turn === 'white' ? 'Beyaz' : 'Siyah'}`;
            if(state.isGameOver) {
                const winner_text = state.winner ? `${state.winner === 'white' ? match.white : match.black} Kazandı` : 'Berabere';
                turnText = `Maç Bitti! Sonuç: ${winner_text}. Sonraki maç başlıyor...`;
            }
            matchInfoElement.innerHTML = `Maç ${state.currentMatchIndex + 1}/${state.schedule.length}: <strong>${match.white} (Beyaz)</strong> vs <strong>${match.black} (Siyah)</strong> - ${turnText}`;
        } else {
            matchInfoElement.textContent = "Turnuva tamamlandı!";
        }

        if(scoreboardBody) {
            scoreboardBody.innerHTML = '';
            const sortedScores = Object.entries(state.scores).sort((a, b) => b[1].points - a[1].points);
            for (const [name, score] of sortedScores) {
                const row = `<tr><td>${name}</td><td>${score.wins}</td><td>${score.draws}</td><td>${score.losses}</td><td>${score.points}</td></tr>`;
                scoreboardBody.innerHTML += row;
            }
        }

        if(scheduleBody) {
            scheduleBody.innerHTML = '';
            state.schedule.forEach((match, index) => {
                let resultText = '-';
                let moveCountText = '-';
                if (match.result) {
                    resultText = match.result;
                    moveCountText = match.move_count;
                }
                const row = `<tr class="${index === state.currentMatchIndex ? 'current-match' : ''}"><td>${match.white}</td><td>${match.black}</td><td>${resultText}</td><td>${moveCountText}</td></tr>`;
                scheduleBody.innerHTML += row;
            });
        }
    }

    async function runTournamentLoop() {
        try {
            const response = await fetch('/tournament/tick', { method: 'POST' });
            const state = await response.json();
            updateUI(state);

            if (state.isRunning) {
                setTimeout(runTournamentLoop, 500);
            }
        } catch (error) {
            console.error("Turnuva döngüsü hatası:", error);
            if(matchInfoElement) matchInfoElement.textContent = "Hata: Turnuva durduruldu.";
        }
    }

    if(startBtn) {
        startBtn.addEventListener('click', async () => {
            startBtn.disabled = true;
            startBtn.textContent = 'Başlatılıyor...';
            try {
                const response = await fetch('/tournament/start', { method: 'POST' });
                const state = await response.json();
                updateUI(state);
                runTournamentLoop();
            } catch (error) {
                console.error("Turnuva başlatılamadı:", error);
                if(matchInfoElement) matchInfoElement.textContent = "Hata: Turnuva başlatılamadı.";
                startBtn.disabled = false;
                startBtn.textContent = 'Turnuvayı Başlat';
            }
        });
    }
});
