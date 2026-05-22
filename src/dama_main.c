// src/dama_main.c
#include "dama_ai.h"
#include "dama_config.h"
#include "dama_game.h"
#include "dama_renderer.h"
#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
  printf("[MAIN] Uygulama başlatılıyor...\n");

  // Renderer ve Game nesnelerini oluştur
  printf("[MAIN] Renderer oluşturuluyor...\n");
  Renderer *renderer = Renderer_Create();
  if (renderer == NULL) {
    printf("[MAIN] HATA: Renderer oluşturma başarısız. Uygulama sonlandırılıyor.\n");
    return 1;
  }
  printf("[MAIN] Renderer başarıyla oluşturuldu.\n");

  // AI Modülünü başlat
  AI_Init();
  printf("[MAIN] AI Modülü başlatıldı.\n");

  printf("[MAIN] Game nesnesi oluşturuluyor...\n");
  Game *game = Game_Create();
  if (game == NULL) {
    printf("[MAIN] HATA: Game nesnesi oluşturma başarısız. Uygulama sonlandırılıyor.\n");
    Renderer_Destroy(renderer);
    return 1;
  }
  printf("[MAIN] Game nesnesi başarıyla oluşturuldu.\n");

  bool gameIsRunning = true;
  SDL_Event event;

  printf("[MAIN] Ana oyun döngüsü başlatılıyor.\n");
  // Ana Oyun Döngüsü
  while (gameIsRunning) {
    // Olayları işle
    while (SDL_PollEvent(&event)) {
      if (event.type == SDL_EVENT_QUIT) {
        printf("[MAIN] Olay algılandı: SDL_EVENT_QUIT (Kapatma isteği)\n");
        gameIsRunning = false;
      }
      if (event.type == SDL_EVENT_MOUSE_BUTTON_DOWN) {
        printf("[MAIN] Olay algılandı: SDL_EVENT_MOUSE_BUTTON_DOWN (Fare tıklaması)\n");

        // SDL3 Logical Presentation kullanıldığı için pencere koordinatlarını
        // mantıksal renderer koordinatlarına çevirmeliyiz.
        float logicalX, logicalY;
        SDL_RenderCoordinatesFromWindow(renderer->renderer, event.button.x,
                                        event.button.y, &logicalX, &logicalY);

        int mouseX = (int)logicalX;
        int mouseY = (int)logicalY;

        printf("[MAIN] Koord: Pencere(%.1f, %.1f) -> Mantiksal(%d, %d)\n",
               event.button.x, event.button.y, mouseX, mouseY);

        // Pondering'i durdur (Oyuncu hamle yapmaya çalışıyor olabilir)
        if (game->currentState == STATE_IN_GAME && game->isPvE &&
            game->currentPlayer != game->aiPlayer) {
          AI_StopPondering();
        }

        // Tıklama olayını oyun durumuna göre yönet
        if (game->currentState == STATE_MAIN_MENU) {
          Game_HandleMenuClick(game, mouseX, mouseY);
        } else if (game->currentState == STATE_IN_GAME) {
          // Tıklamayı oyun tahtası mantığına gönder
          Game_HandleClick(game, mouseX, mouseY);
        } else if (game->currentState == STATE_GAME_OVER) {
          printf("[MAIN] Oyun sonu ekranına tıklandı. Ana menüye dönülüyor.\n");
          // Oyun sonu ekranında herhangi bir yere tıklamak ana menüye döndürür
          Game_Reset(game);
        }
      }
    }

    // Pencere başlığını oyun durumuna göre güncelle
    char title[100];
    if (game->currentState == STATE_IN_GAME) {
      if (game->language == 0) {
        sprintf(title, "Turk Damasi - Sira: %s %s",
                (game->currentPlayer == 1) ? "Beyaz" : "Siyah",
                game->isCaptureMandatory ? "(Zorunlu Yeme!)" : "");
      } else {
        sprintf(title, "Turkish Checkers - Turn: %s %s",
                (game->currentPlayer == 1) ? "White" : "Black",
                game->isCaptureMandatory ? "(Mandatory Capture!)" : "");
      }
    } else if (game->currentState == STATE_GAME_OVER) {
      if (game->language == 0) {
        if (game->winner == 3) {
          sprintf(title, "Oyun Bitti! Beraberlik (Gayyım)");
        } else {
          sprintf(title, "Oyun Bitti! Kazanan: %s",
                  (game->winner == 1) ? "Beyaz" : "Siyah");
        }
      } else {
        if (game->winner == 3) {
          sprintf(title, "Game Over! Draw (Gayyım)");
        } else {
          sprintf(title, "Game Over! Winner: %s",
                  (game->winner == 1) ? "White" : "Black");
        }
      }
    } else {
      if (game->language == 0) {
        sprintf(title, "Turk Damasi - Ana Menu");
      } else {
        sprintf(title, "Turkish Checkers - Main Menu");
      }
    }
    SDL_SetWindowTitle(renderer->window, title);

    // Ekranı çiz
    Renderer_Draw(renderer, game);

    // Pondering: Eğer sıra oyuncudaysa ve henüz düşünmüyorsa, düşünmeyi başlat
    if (game->currentState == STATE_IN_GAME && game->isPvE &&
        game->currentPlayer != game->aiPlayer) {
      AI_StartPondering(game);
    }

    // AI Hamlesi Kontrolü
    if (game->currentState == STATE_IN_GAME && game->isPvE &&
        game->currentPlayer == game->aiPlayer) {

      // Sıra AI'ya geçti, Pondering'i durdur
      AI_StopPondering();

      // Basit bir gecikme ve render update için AI hamlesi hesapla
      printf("[MAIN] AI sırası, hamle hesaplanıyor...\n");
      Renderer_Draw(renderer, game);
      SDL_PumpEvents(); // Event queue'yu canlı tut

      Hamle bestMove = AI_GetBestMove(game);
      if (bestMove.from.row != -1) {
        printf("[MAIN] AI Hamlesi uygulanıyor: (%d,%d)->(%d,%d)\n",
               bestMove.from.row, bestMove.from.col, bestMove.to.row,
               bestMove.to.col);
        bool wasCapture = game->isCaptureMandatory;
        Game_MakeMove(game, bestMove.from, bestMove.to);

        if (wasCapture) {
          Renderer_Draw(renderer, game);
          SDL_Delay(1000);
        }
      } else {
        printf("[MAIN] AI geçerli hamle bulamadı!\n");
      }
    }

    // CPU kullanımını düşürmek için küçük bir gecikme
    SDL_Delay(16);
  }

  // Uygulama kapanırken pondering'i durdur
  AI_StopPondering();

  printf("[MAIN] Ana oyun döngüsü sonlandırıldı. Temizlik yapılıyor...\n");
  // Belleği temizle
  Game_Destroy(game);
  Renderer_Destroy(renderer);

  printf("[MAIN] Uygulama başarıyla sonlandırıldı.\n");

  return 0;
}
