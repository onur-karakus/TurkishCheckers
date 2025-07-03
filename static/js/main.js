// static/js/main.js

import Game from './game.js';

/**
 * Uygulamanın ana giriş noktası.
 * Sayfa yüklendiğinde oyunu başlatır.
 */
document.addEventListener('DOMContentLoaded', () => {
    // initialGameState, HTML şablonu içinde global olarak tanımlanır.
    if (typeof initialGameState !== 'undefined') {
        const game = new Game(initialGameState);
        game.init();
    }
});
