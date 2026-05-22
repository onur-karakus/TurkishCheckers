// DamaC/include/dama_ai.h
#ifndef DAMA_AI_H
#define DAMA_AI_H

#include "dama_game.h"

// AI'nın kullanacağı maksimum derinlik (zorluk seviyesi)
#define AI_DEFAULT_DEPTH 6

/**
 * @brief AI modülünü başlatır. Zobrist anahtarlarını vs. hazırlar.
 */
void AI_Init();

// En iyi hamleyi bul (Normal sıra AI'dayken çağrılır)
Hamle AI_GetBestMove(const Game *game);

// Arka plan düşünmeyi başlat (Sıra oyuncudayken çağrılır)
void AI_StartPondering(const Game *game);

// Arka plan düşünmeyi durdur (Sıra AI'ya geçtiğinde veya oyun bittiğinde çağrılır)
void AI_StopPondering();

#endif // DAMA_AI_H
