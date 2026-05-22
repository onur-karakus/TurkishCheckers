// DamaC/include/dama_renderer.h
#ifndef DAMA_RENDERER_H
#define DAMA_RENDERER_H

#include <SDL3/SDL.h>
#include "dama_game.h"

// --- Veri Yapıları ---

// SDL penceresi, renderer ve font gibi çizimle ilgili tüm kaynakları bir arada tutar.
typedef struct {
    SDL_Window* window;
    SDL_Renderer* renderer;
    SDL_Texture* fontTexture;
    SDL_Texture* circleTexture;
} Renderer;


// --- Fonksiyon Protototipleri ---

/**
 * @brief Renderer nesnesi oluşturur, SDL'i başlatır, pencere ve renderer'ı ayarlar.
 * @return Başarılı olursa oluşturulan Renderer nesnesinin işaretçisi, hata olursa NULL.
 */
Renderer* Renderer_Create();

/**
 * @brief Renderer nesnesini ve tüm SDL kaynaklarını (pencere, renderer, texture) yok eder.
 * @param renderer Yok edilecek renderer nesnesi.
 */
void Renderer_Destroy(Renderer* renderer);

/**
 * @brief Mevcut oyun durumuna göre ekranı çizer.
 * Ana menü, oyun ekranı veya oyun sonu ekranını uygun şekilde render eder.
 * @param renderer Çizim için kullanılacak renderer nesnesi.
 * @param game Çizilecek oyunun anlık durumunu içeren nesne.
 */
void Renderer_Draw(const Renderer* renderer, const Game* game);

#endif // DAMA_RENDERER_H
