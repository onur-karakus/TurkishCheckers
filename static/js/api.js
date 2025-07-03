// static/js/api.js

/**
 * Sunucu ile olan tüm API iletişimini yönetir.
 */
export default class APIClient {
    async request(url, method = 'POST', body = {}) {
        try {
            const options = { method, headers: { 'Content-Type': 'application/json' } };
            if (Object.keys(body).length) options.body = JSON.stringify(body);
            const response = await fetch(url, options);
            if (!response.ok) throw new Error(`Sunucu Hatası: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`[API] ${method} ${url} <- Hata:`, error);
            return null;
        }
    }
    startGame(settings) { return this.request('/api/start_game', 'POST', settings); }
    resignGame() { return this.request('/api/resign', 'POST'); }
    playMove(start, end, timeLeft) { return this.request('/api/play', 'POST', { start, end, time_left: timeLeft }); }
    fetchAIMove() { return this.request('/api/ai_move', 'POST'); }
    fetchValidMoves(r, c) { return this.request(`/api/valid_moves/${r}/${c}`, 'GET'); }
    fetchBackgroundAnalysis() { return this.request('/api/get_analysis', 'GET'); }
}
