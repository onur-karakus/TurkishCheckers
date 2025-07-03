// static/js/game.js

import APIClient from './api.js';
import UIManager from './ui.js';

/**
 * Oyunun ana mantığını, durumunu ve akışını yönetir.
 * API ve UI modüllerini bir araya getirir.
 */
export default class Game {
    constructor(initialGameState) {
        this.gameState = initialGameState;
        this.isRequestPending = false;
        this.analysisInterval = null;
        this.isAnalysisRunning = false;
        this.ui = new UIManager();
        this.api = new APIClient();
    }

    async init() {
        this.bindEvents();
        await this.updateFullUI(this.gameState);
    }

    bindEvents() {
        // DÜZELTME: Panel olayları için dinleyiciyi etkinleştir.
        this.ui.bindPanelEvents();
        
        document.getElementById('start-game-btn')?.addEventListener('click', () => this.handleStartNewGame());
        document.getElementById('resign-btn')?.addEventListener('click', () => this.handleResign());
        this.ui.elements.board?.addEventListener('click', (e) => this.handleSquareClick(e));
        window.addEventListener('resize', () => this.ui.calculateSquarePositions());
    }

    async handleStartNewGame() {
        if (this.isRequestPending) return;
        this.isRequestPending = true;
        this.stopBackgroundAnalysis();
        const settings = {
            mode: this.gameState.mode,
            difficulty: this.ui.elements.difficultySlider.value,
            player_color: document.querySelector('.color-option.active').dataset.color
        };
        const data = await this.api.startGame(settings);
        this.isRequestPending = false;
        if (data) await this.updateFullUI(data);
    }

    async handleResign() {
        if (this.isRequestPending) return;
        this.isRequestPending = true;
        this.stopBackgroundAnalysis();
        const data = await this.api.resignGame();
        this.isRequestPending = false;
        if (data) await this.updateFullUI(data);
    }

    async handleSquareClick(e) {
        if (!this.isHumanTurn() || this.isRequestPending) return;
        const square = e.target.closest('.square');
        if (!square) return;
        this.stopBackgroundAnalysis();
        if (this.ui.selectedSquare) {
            if (square.classList.contains('valid-move')) {
                const startPos = {row: parseInt(this.ui.selectedSquare.dataset.row), col: parseInt(this.ui.selectedSquare.dataset.col)};
                const endPos = {row: parseInt(square.dataset.row), col: parseInt(square.dataset.col)};
                this.ui.clearSelection();
                this.isRequestPending = true;
                const data = await this.api.playMove(startPos, endPos);
                this.isRequestPending = false;
                if (data) await this.processNewGameState(data);
            } else {
                this.ui.clearSelection();
            }
        } else {
            const piece = square.querySelector('.piece');
            if (piece && piece.className.includes(this.gameState.current_player === 'W' ? 'white' : 'black')) {
                this.ui.selectSquare(square);
                const { row, col } = {row: parseInt(square.dataset.row), col: parseInt(square.dataset.col)};
                const data = await this.api.fetchValidMoves(row, col);
                if (data && data.moves) this.ui.highlightValidMoves(data.moves);
                else this.ui.clearSelection();
            }
        }
    }

    async processNewGameState(data) {
        const isAnimationNeeded = data.move_path && data.move_path.length > 0;
        if (isAnimationNeeded) await this.ui.animateMove(data);
        await this.updateFullUI(data);
    }

    async checkAITurn() {
        if (this.isHumanTurn() || !this.gameState.is_active || this.gameState.game_over || this.isRequestPending) return;
        this.isRequestPending = true;
        this.stopBackgroundAnalysis();
        this.ui.clearArrow();
        this.ui.updateMessage("Bilgisayar düşünüyor...", true);
        const data = await this.api.fetchAIMove();
        this.isRequestPending = false;
        if (data) await this.processNewGameState(data);
    }

    async updateFullUI(data) {
        this.gameState = data;
        this.ui.updateUIState(this.gameState);
        await this.ui.drawBoard(this.gameState.board);
        this.ui.updateMessage(this.gameState.message);
        this.ui.updatePlayerIndicators(this.gameState);
        this.ui.updateNotationPanel(this.gameState.move_notations);
        if (this.gameState.is_active && !this.gameState.game_over) {
            if (this.gameState.analysis) {
                this.ui.updateAnalysisPanel(this.gameState.analysis, this.gameState.current_player);
            }
            if (this.isHumanTurn()) {
                this.startBackgroundAnalysis();
            } else {
                this.checkAITurn();
            }
        }
    }

    startBackgroundAnalysis() {
        this.stopBackgroundAnalysis();
        if (this.gameState.game_over || !this.isHumanTurn()) return;
        this.analysisInterval = setInterval(async () => {
            if (this.isAnalysisRunning || this.isRequestPending || !this.isHumanTurn()) return;
            this.isAnalysisRunning = true;
            try {
                const analysisData = await this.api.fetchBackgroundAnalysis();
                if (analysisData && !analysisData.error) {
                    this.ui.updateAnalysisPanel(analysisData, this.gameState.current_player);
                }
            } finally {
                this.isAnalysisRunning = false;
            }
        }, 3000);
    }

    stopBackgroundAnalysis() {
        if (this.analysisInterval) {
            clearInterval(this.analysisInterval);
            this.analysisInterval = null;
        }
    }
    
    isHumanTurn() {
        if (!this.gameState.is_active || this.gameState.game_over) return false;
        if (this.gameState.mode === 'pvp') return true;
        return this.gameState.current_player === this.gameState.player_color;
    }
}
