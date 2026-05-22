// DamaC/src/dama_renderer.c

#include "dama_renderer.h"
#include <SDL3/SDL_error.h> // SDL_GetError için eklendi
#include <SDL3/SDL_hints.h> // SDL_SetHint için eklendi
#include <stdio.h>          // sprintf için
#include <stdlib.h>         // malloc ve free için eklendi
#include <string.h>         // strlen için eklendi
#include <time.h>           // Zaman damgalı loglar için eklendi
#include <math.h>           // Analitik Anti-Aliasing (sqrtf) için eklendi

// --- Dahili Fonksiyon Prototipleri (Bu dosyaya özel) ---
static void logMessage(const char *prefix, const char *message);
static void DrawText(SDL_Renderer *renderer, SDL_Texture *fontTexture,
                     const char *text, int x, int y, float scale,
                     SDL_Color color);
static void DrawCircle(SDL_Renderer *renderer, SDL_Texture *circleTexture, float cX, float cY, float r);
static void DrawBoard(SDL_Renderer *renderer);
static void DrawPiecesAndHighlights(SDL_Renderer *renderer, SDL_Texture *circleTexture, const Game *game);
static void DrawLastMoveHighlight(SDL_Renderer *renderer, const Game *game);
static void DrawGameScene(SDL_Renderer *renderer, SDL_Texture *fontTexture,
                          SDL_Texture *circleTexture, const Game *game);
static void DrawMainMenuScene(SDL_Renderer *renderer, SDL_Texture *fontTexture,
                               const Game *game);
static void DrawGameOverScene(SDL_Renderer *renderer, SDL_Texture *fontTexture,
                               const Game *game);
static SDL_Texture *CreateFontTexture(SDL_Renderer *renderer);
static SDL_Texture *CreateCircleTexture(SDL_Renderer *renderer);
static void DrawPowerBar(SDL_Renderer *renderer, SDL_Texture *fontTexture,
                         const Game *game);

// --- Hata Ayıklama Log Fonksiyonu ---
static void logMessage(const char *prefix, const char *message) {
  time_t rawtime;
  struct tm *timeinfo;
  char buffer[80];
  time(&rawtime);
  timeinfo = localtime(&rawtime);
  strftime(buffer, sizeof(buffer), "[%H:%M:%S]", timeinfo);
  printf("%s %s: %s\n", buffer, prefix, message);
}

// --- Harici (Public) Fonksiyonlar ---

Renderer *Renderer_Create() {
  logMessage("[RENDERER]", "Renderer nesnesi için bellek ayrılıyor...");
  Renderer *renderer = (Renderer *)malloc(sizeof(Renderer));
  if (!renderer) {
    logMessage("[RENDERER]", "HATA: Renderer nesnesi için bellek ayrılamadı!");
    return NULL;
  }

  // SDL3: SDL_Init returns true on success, false on failure.
  if (!SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS)) {
    char errorLog[256];
    sprintf(errorLog, "HATA: SDL_Init başarısız oldu. SDL_GetError(): '%s'",
            SDL_GetError());
    logMessage("[RENDERER]", errorLog);
    free(renderer);
    return NULL;
  }
  logMessage("[RENDERER]", "SDL_Init başarıyla tamamlandı.");

  // HiDPI ve Ölçeklenebilirlik desteği ekliyoruz:
  renderer->window =
      SDL_CreateWindow(WINDOW_TITLE, SCREEN_WIDTH, SCREEN_HEIGHT,
                       SDL_WINDOW_RESIZABLE | SDL_WINDOW_HIGH_PIXEL_DENSITY);
  if (!renderer->window) {
    char errorLog[256];
    sprintf(errorLog, "HATA: Pencere oluşturulamadı. SDL_GetError(): '%s'",
            SDL_GetError());
    logMessage("[RENDERER]", errorLog);
    SDL_Quit();
    free(renderer);
    return NULL;
  }
  logMessage("[RENDERER]", "SDL penceresi (HiDPI etkin) başarıyla oluşturuldu.");

  renderer->renderer = SDL_CreateRenderer(renderer->window, NULL);
  if (!renderer->renderer) {
    char errorLog[256];
    sprintf(errorLog, "HATA: Renderer oluşturulamadı. SDL_GetError(): '%s'",
            SDL_GetError());
    logMessage("[RENDERER]", errorLog);
    SDL_DestroyWindow(renderer->window);
    SDL_Quit();
    free(renderer);
    return NULL;
  }

  // Mantıksal Çözünürlüğü 2x (1600x1800) olarak ayarlıyoruz:
  // SDL3 bunu pencerenin arkasındaki yüksek pikselli Retina tamponuna pürüzsüzce çizer.
  SDL_SetRenderLogicalPresentation(renderer->renderer, LOGICAL_WIDTH,
                                   LOGICAL_HEIGHT,
                                   SDL_LOGICAL_PRESENTATION_LETTERBOX);
  logMessage("[RENDERER]", "SDL renderer ve 2x Mantıksal Çözünürlük başarıyla oluşturuldu.");

  if (!SDL_SetRenderVSync(renderer->renderer, 1)) {
    logMessage("[RENDERER]", "UYARI: V-Sync etkinleştirilemedi.");
  }

  renderer->fontTexture = CreateFontTexture(renderer->renderer);
  if (!renderer->fontTexture) {
    logMessage("[RENDERER]", "HATA: Font texture oluşturulamadı!");
    Renderer_Destroy(renderer);
    return NULL;
  }
  logMessage("[RENDERER]", "Font texture başarıyla oluşturuldu.");

  renderer->circleTexture = CreateCircleTexture(renderer->renderer);
  if (!renderer->circleTexture) {
    logMessage("[RENDERER]", "HATA: Daire texture oluşturulamadı!");
    Renderer_Destroy(renderer);
    return NULL;
  }
  logMessage("[RENDERER]", "Daire texture başarıyla oluşturuldu.");

  return renderer;
}

void Renderer_Destroy(Renderer *renderer) {
  if (renderer) {
    logMessage("[RENDERER]", "Renderer nesnesi ve SDL kaynakları yok ediliyor...");
    if (renderer->fontTexture)
      SDL_DestroyTexture(renderer->fontTexture);
    if (renderer->circleTexture)
      SDL_DestroyTexture(renderer->circleTexture);
    if (renderer->renderer)
      SDL_DestroyRenderer(renderer->renderer);
    if (renderer->window)
      SDL_DestroyWindow(renderer->window);
    free(renderer);
    logMessage("[RENDERER]", "Tüm kaynaklar serbest bırakıldı.");
  }
  SDL_Quit();
}

void Renderer_Draw(const Renderer *renderer, const Game *game) {
  // Arka plan rengini hoş bir açık gri yapıyoruz
  SDL_SetRenderDrawColor(renderer->renderer, 230, 232, 235, 255);
  SDL_RenderClear(renderer->renderer);

  switch (game->currentState) {
  case STATE_MAIN_MENU:
    DrawMainMenuScene(renderer->renderer, renderer->fontTexture, game);
    break;
  case STATE_IN_GAME:
    DrawGameScene(renderer->renderer, renderer->fontTexture, renderer->circleTexture, game);
    break;
  case STATE_GAME_OVER:
    DrawGameOverScene(renderer->renderer, renderer->fontTexture, game);
    break;
  }

  SDL_RenderPresent(renderer->renderer);
}

// --- Dahili Çizim Fonksiyonları ---

static void DrawPowerBar(SDL_Renderer *renderer, SDL_Texture *fontTexture,
                         const Game *game) {
  Scores current_scores = game->scores;
  int totalScore = current_scores.white + current_scores.black;
  if (totalScore == 0)
    return; // Sıfıra bölme hatasını önle

  float whiteRatio = (float)current_scores.white / totalScore;

  // Çubuğun konumu ve boyutları (2x ölçeklenmiş)
  float barWidth = BOARD_AREA_SIZE;
  float barHeight = 40.0f; // 20.0f * 2
  float barX = BOARD_OFFSET;
  float barY = BOARD_OFFSET + BOARD_AREA_SIZE + 50; // 25 * 2

  // Arka plan (çerçeve)
  SDL_FRect borderRect = {barX - 4, barY - 4, barWidth + 8, barHeight + 8};
  SDL_SetRenderDrawColor(renderer, 80, 80, 85, 255); // Koyu gri çerçeve
  SDL_RenderFillRect(renderer, &borderRect);

  // Siyah oyuncunun gücü (arka planın tamamı)
  SDL_FRect blackRect = {barX, barY, barWidth, barHeight};
  SDL_SetRenderDrawColor(renderer, 30, 30, 30, 255); // Koyu Antrasit
  SDL_RenderFillRect(renderer, &blackRect);

  // Beyaz oyuncunun gücü (siyahın üzerine çizilir)
  if (whiteRatio > 0) {
    float whiteWidth = barWidth * whiteRatio;
    SDL_FRect whiteRect = {barX, barY, whiteWidth, barHeight};
    SDL_SetRenderDrawColor(renderer, 245, 245, 247, 255); // Premium Beyaz
    SDL_RenderFillRect(renderer, &whiteRect);
  }
}

static SDL_Texture *CreateFontTexture(SDL_Renderer *renderer) {
  // 128-139 arası Türkçe karakterler için ayrıldı
  // ç=128, ğ=129, ı=130, ö=131, ş=132, ü=133
  // Ç=134, Ğ=135, İ=136, Ö=137, Ş=138, Ü=139
  unsigned char font_data[256][8] = {0};

  // ASCII (Basic)
  const unsigned char ascii_data[128][8] = {
      [' '] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
      ['!'] = {0x18, 0x18, 0x18, 0x18, 0x00, 0x18, 0x18, 0x00},
      ['('] = {0x0C, 0x18, 0x30, 0x30, 0x30, 0x18, 0x0C, 0x00},
      [')'] = {0x30, 0x18, 0x0C, 0x0C, 0x0C, 0x18, 0x30, 0x00},
      [':'] = {0x00, 0x36, 0x36, 0x00, 0x36, 0x36, 0x00, 0x00},
      ['?'] = {0x3C, 0x66, 0x0C, 0x18, 0x18, 0x00, 0x18, 0x00},
      ['<'] = {0x0C, 0x18, 0x30, 0x60, 0x30, 0x18, 0x0C, 0x00},
      ['>'] = {0x30, 0x18, 0x0C, 0x06, 0x0C, 0x18, 0x30, 0x00},
      ['-'] = {0x00, 0x00, 0x00, 0x7E, 0x00, 0x00, 0x00, 0x00},
      ['.'] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x18, 0x00},
      ['/'] = {0x00, 0x03, 0x06, 0x0C, 0x18, 0x30, 0x60, 0x00},
      
      // Numbers
      ['0'] = {0x3E, 0x63, 0x73, 0x7B, 0x6F, 0x67, 0x3E, 0x00},
      ['1'] = {0x18, 0x38, 0x18, 0x18, 0x18, 0x18, 0x3C, 0x00},
      ['2'] = {0x3C, 0x66, 0x06, 0x0C, 0x18, 0x30, 0x7E, 0x00},
      ['3'] = {0x3C, 0x66, 0x06, 0x1C, 0x06, 0x66, 0x3C, 0x00},
      ['4'] = {0x0C, 0x1C, 0x2C, 0x4C, 0x7E, 0x0C, 0x0C, 0x00},
      ['5'] = {0x7E, 0x60, 0x7C, 0x06, 0x06, 0x66, 0x3C, 0x00},
      ['6'] = {0x3C, 0x60, 0x60, 0x7C, 0x66, 0x66, 0x3C, 0x00},
      ['7'] = {0x7E, 0x06, 0x0C, 0x18, 0x30, 0x30, 0x30, 0x00},
      ['8'] = {0x3C, 0x66, 0x66, 0x3C, 0x66, 0x66, 0x3C, 0x00},
      ['9'] = {0x3C, 0x66, 0x66, 0x3E, 0x06, 0x06, 0x3C, 0x00},

      // Uppercase Letters
      ['A'] = {0x3C, 0x66, 0x66, 0x7E, 0x66, 0x66, 0x66, 0x00},
      ['B'] = {0x7C, 0x66, 0x66, 0x7C, 0x66, 0x66, 0x7C, 0x00},
      ['C'] = {0x3E, 0x62, 0x60, 0x60, 0x60, 0x62, 0x3E, 0x00},
      ['D'] = {0x7C, 0x66, 0x66, 0x66, 0x66, 0x66, 0x7C, 0x00},
      ['E'] = {0x7E, 0x60, 0x60, 0x7C, 0x60, 0x60, 0x7E, 0x00},
      ['F'] = {0x7E, 0x60, 0x60, 0x7C, 0x60, 0x60, 0x60, 0x00},
      ['G'] = {0x3E, 0x62, 0x60, 0x6E, 0x66, 0x66, 0x3E, 0x00},
      ['H'] = {0x66, 0x66, 0x66, 0x7E, 0x66, 0x66, 0x66, 0x00},
      ['I'] = {0x3C, 0x18, 0x18, 0x18, 0x18, 0x18, 0x3C, 0x00},
      ['J'] = {0x1E, 0x0C, 0x0C, 0x0C, 0x0C, 0xCC, 0x78, 0x00},
      ['K'] = {0x66, 0x6C, 0x78, 0x70, 0x78, 0x6C, 0x66, 0x00},
      ['L'] = {0x60, 0x60, 0x60, 0x60, 0x60, 0x60, 0x7E, 0x00},
      ['M'] = {0x63, 0x77, 0x7F, 0x6B, 0x63, 0x63, 0x63, 0x00},
      ['N'] = {0x66, 0x76, 0x7E, 0x7E, 0x6E, 0x66, 0x66, 0x00},
      ['O'] = {0x3C, 0x66, 0x66, 0x66, 0x66, 0x66, 0x3C, 0x00},
      ['P'] = {0x7C, 0x66, 0x66, 0x7C, 0x60, 0x60, 0x60, 0x00},
      ['Q'] = {0x3C, 0x66, 0x66, 0x66, 0x6E, 0x3C, 0x0E, 0x00},
      ['R'] = {0x7C, 0x66, 0x66, 0x7C, 0x78, 0x6C, 0x66, 0x00},
      ['S'] = {0x3E, 0x60, 0x60, 0x3C, 0x06, 0x06, 0x7C, 0x00},
      ['T'] = {0x7E, 0x7E, 0x18, 0x18, 0x18, 0x18, 0x18, 0x00},
      ['U'] = {0x66, 0x66, 0x66, 0x66, 0x66, 0x66, 0x3C, 0x00},
      ['V'] = {0x66, 0x66, 0x66, 0x66, 0x66, 0x3C, 0x18, 0x00},
      ['W'] = {0x63, 0x63, 0x63, 0x6B, 0x7F, 0x77, 0x63, 0x00},
      ['X'] = {0x66, 0x66, 0x3C, 0x18, 0x3C, 0x66, 0x66, 0x00},
      ['Y'] = {0x66, 0x66, 0x66, 0x3C, 0x18, 0x18, 0x18, 0x00},
      ['Z'] = {0x7E, 0x06, 0x0C, 0x18, 0x30, 0x60, 0x7E, 0x00},

      // Lowercase Letters
      ['a'] = {0x00, 0x00, 0x3C, 0x06, 0x3E, 0x66, 0x3E, 0x00},
      ['b'] = {0x60, 0x60, 0x7C, 0x66, 0x66, 0x66, 0x7C, 0x00},
      ['c'] = {0x00, 0x00, 0x3C, 0x66, 0x60, 0x66, 0x3C, 0x00},
      ['d'] = {0x06, 0x06, 0x3E, 0x66, 0x66, 0x66, 0x3E, 0x00},
      ['e'] = {0x00, 0x00, 0x3C, 0x66, 0x7E, 0x60, 0x3C, 0x00},
      ['f'] = {0x1E, 0x30, 0x30, 0x7C, 0x30, 0x30, 0x30, 0x00},
      ['g'] = {0x00, 0x00, 0x3E, 0x66, 0x66, 0x3E, 0x06, 0x3C},
      ['h'] = {0x60, 0x60, 0x7C, 0x66, 0x66, 0x66, 0x66, 0x00},
      ['i'] = {0x18, 0x00, 0x18, 0x18, 0x18, 0x18, 0x18, 0x00},
      ['j'] = {0x0C, 0x00, 0x0C, 0x0C, 0x0C, 0x0C, 0xCC, 0x78},
      ['k'] = {0x60, 0x60, 0x6C, 0x78, 0x78, 0x6C, 0x66, 0x00},
      ['l'] = {0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x3C, 0x00},
      ['m'] = {0x00, 0x00, 0x66, 0x7E, 0x7E, 0x6B, 0x6B, 0x00},
      ['n'] = {0x00, 0x00, 0x7C, 0x66, 0x66, 0x66, 0x66, 0x00},
      ['o'] = {0x00, 0x00, 0x3C, 0x66, 0x66, 0x66, 0x3C, 0x00},
      ['p'] = {0x00, 0x00, 0x7C, 0x66, 0x7C, 0x60, 0x60, 0x00},
      ['q'] = {0x00, 0x00, 0x3E, 0x66, 0x66, 0x3E, 0x06, 0x07},
      ['r'] = {0x00, 0x00, 0x7C, 0x6E, 0x60, 0x60, 0x60, 0x00},
      ['s'] = {0x00, 0x00, 0x3E, 0x60, 0x3C, 0x06, 0x7C, 0x00},
      ['t'] = {0x18, 0x18, 0x7E, 0x18, 0x18, 0x1C, 0x0C, 0x00},
      ['u'] = {0x00, 0x00, 0x66, 0x66, 0x66, 0x66, 0x3E, 0x00},
      ['v'] = {0x00, 0x00, 0x66, 0x66, 0x66, 0x3C, 0x18, 0x00},
      ['w'] = {0x00, 0x00, 0x63, 0x6B, 0x7F, 0x3E, 0x22, 0x00},
      ['x'] = {0x00, 0x00, 0x66, 0x3C, 0x18, 0x3C, 0x66, 0x00},
      ['y'] = {0x00, 0x00, 0x66, 0x66, 0x3E, 0x06, 0x3C, 0x00},
      ['z'] = {0x00, 0x00, 0x7E, 0x0C, 0x18, 0x30, 0x7E, 0x00},
  };

  // Copy ASCII data
  for (int i = 0; i < 128; i++) {
    for (int j = 0; j < 8; j++) {
      font_data[i][j] = ascii_data[i][j];
    }
  }

  // Turkish Characters
  // ç (128)
  font_data[128][0] = 0x00;
  font_data[128][1] = 0x00;
  font_data[128][2] = 0x3C;
  font_data[128][3] = 0x66;
  font_data[128][4] = 0x60;
  font_data[128][5] = 0x66;
  font_data[128][6] = 0x3C;
  font_data[128][7] = 0x18;

  // ğ (129)
  font_data[129][0] = 0x34;
  font_data[129][1] = 0x00;
  font_data[129][2] = 0x3E;
  font_data[129][3] = 0x66;
  font_data[129][4] = 0x66;
  font_data[129][5] = 0x3E;
  font_data[129][6] = 0x06;
  font_data[129][7] = 0x3C;

  // ı (130)
  font_data[130][0] = 0x00;
  font_data[130][1] = 0x00;
  font_data[130][2] = 0x18;
  font_data[130][3] = 0x18;
  font_data[130][4] = 0x18;
  font_data[130][5] = 0x18;
  font_data[130][6] = 0x18;
  font_data[130][7] = 0x00;

  // ö (131)
  font_data[131][0] = 0x24;
  font_data[131][1] = 0x00;
  font_data[131][2] = 0x3C;
  font_data[131][3] = 0x66;
  font_data[131][4] = 0x66;
  font_data[131][5] = 0x66;
  font_data[131][6] = 0x3C;
  font_data[131][7] = 0x00;

  // ş (132)
  font_data[132][0] = 0x00;
  font_data[132][1] = 0x00;
  font_data[132][2] = 0x3E;
  font_data[132][3] = 0x60;
  font_data[132][4] = 0x3C;
  font_data[132][5] = 0x06;
  font_data[132][6] = 0x7C;
  font_data[132][7] = 0x18;

  // ü (133)
  font_data[133][0] = 0x24;
  font_data[133][1] = 0x00;
  font_data[133][2] = 0x66;
  font_data[133][3] = 0x66;
  font_data[133][4] = 0x66;
  font_data[133][5] = 0x66;
  font_data[133][6] = 0x3E;
  font_data[133][7] = 0x00;

  // Ç (Büyük)
  font_data[134][0] = 0x00;
  font_data[134][1] = 0x3C;
  font_data[134][2] = 0x66;
  font_data[134][3] = 0x60;
  font_data[134][4] = 0x66;
  font_data[134][5] = 0x66;
  font_data[134][6] = 0x3C;
  font_data[134][7] = 0x18;

  // Ğ (135)
  font_data[135][0] = 0x34;
  font_data[135][1] = 0x3C;
  font_data[135][2] = 0x66;
  font_data[135][3] = 0x60;
  font_data[135][4] = 0x6E;
  font_data[135][5] = 0x66;
  font_data[135][6] = 0x3E;
  font_data[135][7] = 0x00;

  // İ (136)
  font_data[136][0] = 0x18;
  font_data[136][1] = 0x3C;
  font_data[136][2] = 0x18;
  font_data[136][3] = 0x18;
  font_data[136][4] = 0x18;
  font_data[136][5] = 0x18;
  font_data[136][6] = 0x3C;
  font_data[136][7] = 0x00;

  // Ö (137)
  font_data[137][0] = 0x24;
  font_data[137][1] = 0x3C;
  font_data[137][2] = 0x66;
  font_data[137][3] = 0x66;
  font_data[137][4] = 0x66;
  font_data[137][5] = 0x66;
  font_data[137][6] = 0x3C;
  font_data[137][7] = 0x00;

  // Ş (138)
  font_data[138][0] = 0x00;
  font_data[138][1] = 0x3E;
  font_data[138][2] = 0x60;
  font_data[138][3] = 0x3C;
  font_data[138][4] = 0x06;
  font_data[138][5] = 0x66;
  font_data[138][6] = 0x3C;
  font_data[138][7] = 0x18;

  // Ü (139)
  font_data[139][0] = 0x24;
  font_data[139][1] = 0x66;
  font_data[139][2] = 0x66;
  font_data[139][3] = 0x66;
  font_data[139][4] = 0x66;
  font_data[139][5] = 0x66;
  font_data[139][6] = 0x3C;
  font_data[139][7] = 0x00;

  const int CHAR_SIZE = 64; // Her bir karakteri 64x64 piksellik yüksek çözünürlükte oluşturuyoruz.
  const int ATLAS_COLS = 16, ATLAS_ROWS = 16;
  SDL_Surface *fontSurface =
      SDL_CreateSurface(ATLAS_COLS * CHAR_SIZE, ATLAS_ROWS * CHAR_SIZE,
                        SDL_PIXELFORMAT_RGBA32);
  if (!fontSurface) {
    logMessage("[RENDERER]", "HATA: Font yüzeyi (surface) oluşturulamadı!");
    return NULL;
  }
  
  SDL_FillSurfaceRect(
      fontSurface, NULL,
      SDL_MapRGBA(SDL_GetPixelFormatDetails(fontSurface->format), NULL, 0, 0, 0, 0));
  
  const SDL_PixelFormatDetails *details = SDL_GetPixelFormatDetails(fontSurface->format);
  Uint32 *pixels = (Uint32 *)fontSurface->pixels;
  
  for (int i = 0; i < 256; i++) {
    int col = i % ATLAS_COLS;
    int row = i / ATLAS_COLS;
    int start_x = col * CHAR_SIZE;
    int start_y = row * CHAR_SIZE;

    // 8x8 piksellik ikili karakter verisini 64x64 piksele bilineer enterpolasyon ve yumuşatma ile büyütüyoruz (Vector-like scaling)
    for (int Y = 0; Y < CHAR_SIZE; Y++) {
      float v = (Y + 0.5f) / CHAR_SIZE;
      float py = v * 8.0f - 0.5f;
      float fy0 = floorf(py);
      int y0 = (int)fy0;
      int y1 = y0 + 1;
      float ty = py - fy0;
      if (y0 < 0) { y0 = 0; y1 = 0; }
      if (y1 > 7) { y0 = 7; y1 = 7; }

      for (int X = 0; X < CHAR_SIZE; X++) {
        float u = (X + 0.5f) / CHAR_SIZE;
        float px = u * 8.0f - 0.5f;
        float fx0 = floorf(px);
        int x0 = (int)fx0;
        int x1 = x0 + 1;
        float tx = px - fx0;
        if (x0 < 0) { x0 = 0; x1 = 0; }
        if (x1 > 7) { x0 = 7; x1 = 7; }

        // 8x8 ikili bitmap'ten değerleri çek
        float v00 = ((font_data[i][y0] >> (7 - x0)) & 1) ? 1.0f : 0.0f;
        float v10 = ((font_data[i][y0] >> (7 - x1)) & 1) ? 1.0f : 0.0f;
        float v01 = ((font_data[i][y1] >> (7 - x0)) & 1) ? 1.0f : 0.0f;
        float v11 = ((font_data[i][y1] >> (7 - x1)) & 1) ? 1.0f : 0.0f;

        // Bilineer Enterpolasyon (Bilinear Interpolation)
        float val = (1.0f - tx) * (1.0f - ty) * v00 +
                    tx * (1.0f - ty) * v10 +
                    (1.0f - tx) * ty * v01 +
                    tx * ty * v11;

        // Hermite s-eğrisi (Smoothstep) kullanarak yumuşak ve kavisli kenarlar elde ediyoruz (Perfect vector-like curves)
        float alpha_f = val * val * (3.0f - 2.0f * val);

        // Hücre kenarlarında taşmayı önlemek için sınırları hafifçe sıfıra yumuşat
        float border_dist_x = (X < CHAR_SIZE / 2) ? (float)X : (float)(CHAR_SIZE - 1 - X);
        float border_dist_y = (Y < CHAR_SIZE / 2) ? (float)Y : (float)(CHAR_SIZE - 1 - Y);
        float min_border = (border_dist_x < border_dist_y) ? border_dist_x : border_dist_y;
        if (min_border < 2.0f) {
          alpha_f *= (min_border / 2.0f);
        }

        Uint8 alpha = (Uint8)(255.0f * alpha_f);
        pixels[(start_y + Y) * fontSurface->w + (start_x + X)] =
            SDL_MapRGBA(details, NULL, 255, 255, 255, alpha);
      }
    }
  }

  SDL_Texture *texture = SDL_CreateTextureFromSurface(renderer, fontSurface);
  if (!texture) {
    logMessage("[RENDERER]", "HATA: Font texture oluşturulamadı!");
    SDL_DestroySurface(fontSurface);
    return NULL;
  }
  
  SDL_SetTextureBlendMode(texture, SDL_BLENDMODE_BLEND);
  
  // Yüksek çözünürlüklü fontumuzu pürüzsüz ölçeklemek için doğrusal (linear) filtreleme uyguluyoruz
  SDL_SetTextureScaleMode(texture, SDL_SCALEMODE_LINEAR);
  
  SDL_DestroySurface(fontSurface);
  return texture;
}

static SDL_Texture *CreateCircleTexture(SDL_Renderer *renderer) {
  int size = 512;
  SDL_Surface *circleSurface = SDL_CreateSurface(size, size, SDL_PIXELFORMAT_RGBA32);
  if (!circleSurface) {
    logMessage("[RENDERER]", "HATA: Daire yüzeyi (surface) oluşturulamadı!");
    return NULL;
  }

  const SDL_PixelFormatDetails *details = SDL_GetPixelFormatDetails(circleSurface->format);
  Uint32 *pixels = (Uint32 *)circleSurface->pixels;
  float center = (size - 1) / 2.0f;
  float radius = (size / 2.0f) - 2.0f;

  for (int y = 0; y < size; y++) {
    float dy = y - center;
    for (int x = 0; x < size; x++) {
      float dx = x - center;
      float dist = sqrtf(dx * dx + dy * dy);
      Uint8 alpha = 0;
      if (dist <= radius - 1.5f) {
        alpha = 255;
      } else if (dist < radius + 1.5f) {
        // 3 piksellik geçiş alanı ile kusursuz pürüzsüzleştirme (3px transition zone for flawless AA)
        float f = (radius + 1.5f - dist) / 3.0f;
        if (f < 0.0f) f = 0.0f;
        if (f > 1.0f) f = 1.0f;
        alpha = (Uint8)(255.0f * f);
      }
      pixels[y * size + x] = SDL_MapRGBA(details, NULL, 255, 255, 255, alpha);
    }
  }

  SDL_Texture *texture = SDL_CreateTextureFromSurface(renderer, circleSurface);
  if (!texture) {
    logMessage("[RENDERER]", "HATA: Daire texture oluşturulamadı!");
    SDL_DestroySurface(circleSurface);
    return NULL;
  }

  SDL_SetTextureBlendMode(texture, SDL_BLENDMODE_BLEND);
  SDL_SetTextureScaleMode(texture, SDL_SCALEMODE_LINEAR); // Linear (bilinear) interpolation

  SDL_DestroySurface(circleSurface);
  return texture;
}

static void DrawText(SDL_Renderer *renderer, SDL_Texture *fontTexture,
                     const char *text, int x, int y, float scale,
                     SDL_Color color) {
  if (!fontTexture)
    return;
  SDL_SetTextureColorMod(fontTexture, color.r, color.g, color.b);
  const int CHAR_SIZE = 64; // Büyütülmüş font atlasındaki kaynak boyutu (Source size)
  const int DISPLAY_SIZE = 8; // Mantıksal düzendeki yerleşim boyutu (Display layout size)
  const int ATLAS_COLS = 16;

  int cursorX = x;

  for (int i = 0; text[i] != '\0'; i++) {
    unsigned char c = (unsigned char)text[i];
    int index = 0;

    // UTF-8 Ayrıştırma (Türkçe Karakterler için)
    if (c < 128) {
      index = c;
    } else {
      unsigned char next = (unsigned char)text[i + 1];
      if (next == '\0')
        break;

      if (c == 0xC3) {
        if (next == 0xA7)
          index = 128; // ç
        else if (next == 0x87)
          index = 134; // Ç
        else if (next == 0xB6)
          index = 131; // ö
        else if (next == 0x96)
          index = 137; // Ö
        else if (next == 0xBC)
          index = 133; // ü
        else if (next == 0x9C)
          index = 139; // Ü
      } else if (c == 0xC4) {
        if (next == 0x9F)
          index = 129; // ğ
        else if (next == 0x9E)
          index = 135; // Ğ
        else if (next == 0xB1)
          index = 130; // ı
        else if (next == 0xB0)
          index = 136; // İ
      } else if (c == 0xC5) {
        if (next == 0x9F)
          index = 132; // ş
        else if (next == 0x9E)
          index = 138; // Ş
      }

      if (index != 0) {
        i++; // Çok baytlı karakterin 2. baytını geç
      } else {
        index = '?'; // Bilinmeyen karakter
      }
    }

    SDL_FRect srcRect = {(float)((index % ATLAS_COLS) * CHAR_SIZE),
                         (float)((index / ATLAS_COLS) * CHAR_SIZE),
                         (float)CHAR_SIZE, (float)CHAR_SIZE};
    SDL_FRect dstRect = {(float)cursorX, (float)y, DISPLAY_SIZE * scale,
                         DISPLAY_SIZE * scale};
    SDL_RenderTexture(renderer, fontTexture, &srcRect, &dstRect);

    cursorX += DISPLAY_SIZE * scale;
  }
}

// Dairesel texture çizim metodu (Kusursuz donanımsal pürüzsüzleştirme)
static void DrawCircle(SDL_Renderer *renderer, SDL_Texture *circleTexture, float cX, float cY, float r) {
  if (!circleTexture)
    return;
  
  Uint8 r_color, g_color, b_color, a_color;
  SDL_GetRenderDrawColor(renderer, &r_color, &g_color, &b_color, &a_color);
  
  SDL_SetTextureColorMod(circleTexture, r_color, g_color, b_color);
  SDL_SetTextureAlphaMod(circleTexture, a_color);
  
  SDL_FRect dstRect = { cX - r, cY - r, r * 2.0f, r * 2.0f };
  SDL_RenderTexture(renderer, circleTexture, NULL, &dstRect);
}

static void DrawBoard(SDL_Renderer *renderer) {
  for (int i = 0; i < 8; i++) {
    for (int j = 0; j < 8; j++) {
      SDL_FRect r = {BOARD_OFFSET + (float)j * SQUARE_SIZE,
                     BOARD_OFFSET + (float)i * SQUARE_SIZE, (float)SQUARE_SIZE,
                     (float)SQUARE_SIZE};
      // Estetik Ahşap ve Akçaağaç tonları kullanan Dama Tahtası
      if ((i + j) % 2 == 0)
        SDL_SetRenderDrawColor(renderer, 242, 226, 203, 255); // Krem
      else
        SDL_SetRenderDrawColor(renderer, 139, 90, 60, 255); // Sıcak Kahve
      SDL_RenderFillRect(renderer, &r);
    }
  }
}

static void DrawPiecesAndHighlights(SDL_Renderer *renderer, SDL_Texture *circleTexture, const Game *game) {
  bool canMove[8][8] = {false};
  for (int i = 0; i < game->moveCount; i++) {
    canMove[game->possibleMoves[i].from.row][game->possibleMoves[i].from.col] =
        true;
  }

  for (int i = 0; i < 8; i++) {
    for (int j = 0; j < 8; j++) {
      if (game->board[i][j] != BOS_KARE) {
        int cX = BOARD_OFFSET + j * SQUARE_SIZE + SQUARE_SIZE / 2;
        int cY = BOARD_OFFSET + i * SQUARE_SIZE + SQUARE_SIZE / 2;
        int r = SQUARE_SIZE / 2 - 20; // 2x ölçek için r güncellendi

        // Hareket edebilecek taşı vurgula (Hoş bir yeşil gölge efektiyle)
        if (canMove[i][j]) {
          SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_BLEND);
          SDL_SetRenderDrawColor(renderer, 46, 204, 113, 100);
          DrawCircle(renderer, circleTexture, cX, cY, r + 10);
        }

        // Taş Gövdesi Çizimi
        if (game->board[i][j] == BEYAZ_TAS || game->board[i][j] == BEYAZ_DAMA) {
          // Beyaz Taş Gövdesi (Hafif Fildişi gölgesiyle)
          SDL_SetRenderDrawColor(renderer, 245, 245, 247, 255);
        } else {
          // Siyah Taş Gövdesi (Koyu Antrasit)
          SDL_SetRenderDrawColor(renderer, 30, 30, 30, 255);
        }
        DrawCircle(renderer, circleTexture, cX, cY, r);

        // İç halka detayı (Taşı daha 3D/Premium gösterir)
        if (game->board[i][j] == BEYAZ_TAS || game->board[i][j] == BEYAZ_DAMA) {
          SDL_SetRenderDrawColor(renderer, 210, 210, 215, 255);
        } else {
          SDL_SetRenderDrawColor(renderer, 60, 60, 60, 255);
        }
        DrawCircle(renderer, circleTexture, cX, cY, r - 12);

        // Dama Taçı (Altın Sarısı göbek)
        if (game->board[i][j] == BEYAZ_DAMA || game->board[i][j] == SIYAH_DAMA) {
          SDL_SetRenderDrawColor(renderer, 241, 196, 15, 255); // Altın
          DrawCircle(renderer, circleTexture, cX, cY, r / 2);
        }
      }
    }
  }

  // Seçili taşın olası hedef karelerini göster (yeşil halkalar)
  if (game->selectedPiece.row != -1) {
    for (int i = 0; i < game->moveCount; i++) {
      if (game->possibleMoves[i].from.row == game->selectedPiece.row &&
          game->possibleMoves[i].from.col == game->selectedPiece.col) {
        Koordinat to = game->possibleMoves[i].to;
        SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_BLEND);
        SDL_SetRenderDrawColor(renderer, 46, 204, 113, 160);
        DrawCircle(renderer, circleTexture,
                   BOARD_OFFSET + to.col * SQUARE_SIZE + SQUARE_SIZE / 2,
                   BOARD_OFFSET + to.row * SQUARE_SIZE + SQUARE_SIZE / 2, 30);
      }
    }
  }
}

static void DrawLastMoveHighlight(SDL_Renderer *renderer, const Game *game) {
  if (game->lastMove.from.row != -1) {
    SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_BLEND);
    SDL_FRect fromRect = {
        BOARD_OFFSET + (float)game->lastMove.from.col * SQUARE_SIZE,
        BOARD_OFFSET + (float)game->lastMove.from.row * SQUARE_SIZE,
        (float)SQUARE_SIZE, (float)SQUARE_SIZE};
    SDL_SetRenderDrawColor(renderer, 52, 152, 219, 60); // Mavi şeffaf kare
    SDL_RenderFillRect(renderer, &fromRect);
    
    SDL_FRect toRect = {
        BOARD_OFFSET + (float)game->lastMove.to.col * SQUARE_SIZE,
        BOARD_OFFSET + (float)game->lastMove.to.row * SQUARE_SIZE,
        (float)SQUARE_SIZE, (float)SQUARE_SIZE};
    SDL_SetRenderDrawColor(renderer, 52, 152, 219, 100);
    SDL_RenderFillRect(renderer, &toRect);
  }
}

static void DrawGameScene(SDL_Renderer *renderer, SDL_Texture *fontTexture,
                          SDL_Texture *circleTexture, const Game *game) {
  DrawBoard(renderer);

  bool isReplay = (game->viewIndex < game->historyCount);

  if (isReplay) {
    Game tempGame = *game;
    memcpy(tempGame.board, game->history[game->viewIndex].board,
           sizeof(tempGame.board));
    tempGame.selectedPiece = (Koordinat){-1, -1};
    tempGame.lastMove = (Hamle){{-1, -1}, {-1, -1}};

    DrawPiecesAndHighlights(renderer, circleTexture, &tempGame);

    // Replay Göstergesi (Metin boyutu 2x ölçeklendi -> 4.0f)
    const char *replay_title = (game->language == 0) ? "GEÇMİŞ İZLENİYOR" : "REPLAY MODE";
    float replay_title_w = strlen(replay_title) * 8 * 4.0f;
    DrawText(renderer, fontTexture, replay_title, LOGICAL_WIDTH / 2 - replay_title_w / 2,
             40, 4.0f, (SDL_Color){231, 76, 60, 255}); // Parlak Kırmızı

    char note[50];
    if (game->language == 0) {
      sprintf(note, "Hamle %d: %s", game->viewIndex,
              game->history[game->viewIndex].notation);
    } else {
      sprintf(note, "Move %d: %s", game->viewIndex,
              game->history[game->viewIndex].notation);
    }
    int w = strlen(note) * 8 * 4.0f;
    DrawText(renderer, fontTexture, note, LOGICAL_WIDTH / 2 - w / 2, 100, 4.0f,
             (SDL_Color){44, 62, 80, 255});

  } else {
    DrawLastMoveHighlight(renderer, game);
    DrawPiecesAndHighlights(renderer, circleTexture, game);
  }

  DrawPowerBar(renderer, fontTexture, game);

  // Koordinatları Çiz (Premium Siyah Font ile 4.0f Ölçekli)
  for (int i = 0; i < 8; i++) {
    char col_char[2] = {'a' + i, '\0'};
    char row_char[2] = {'1' + i, '\0'};
    
    // Üst Harfler
    DrawText(renderer, fontTexture, col_char,
             BOARD_OFFSET + i * SQUARE_SIZE + SQUARE_SIZE / 2 - 8,
             BOARD_OFFSET - 45, 4.0f, (SDL_Color){44, 62, 80, 255});
    // Alt Harfler
    DrawText(renderer, fontTexture, col_char,
             BOARD_OFFSET + i * SQUARE_SIZE + SQUARE_SIZE / 2 - 8,
             BOARD_OFFSET + BOARD_AREA_SIZE + 10, 4.0f,
             (SDL_Color){44, 62, 80, 255});
    // Sol Sayılar
    DrawText(renderer, fontTexture, row_char, BOARD_OFFSET - 45,
             BOARD_OFFSET + i * SQUARE_SIZE + SQUARE_SIZE / 2 - 16, 4.0f,
             (SDL_Color){44, 62, 80, 255});
    // Sağ Sayılar
    DrawText(renderer, fontTexture, row_char,
             BOARD_OFFSET + BOARD_AREA_SIZE + 15,
             BOARD_OFFSET + i * SQUARE_SIZE + SQUARE_SIZE / 2 - 16, 4.0f,
             (SDL_Color){44, 62, 80, 255});
  }

  // Yapay Zeka Düşünüyor Metni (6.0f Ölçekli)
  if (game->isPvE && game->currentPlayer == game->aiPlayer && !isReplay) {
    const char *thinkingText = (game->language == 0) ? "YAPAY ZEKA DÜŞÜNÜYOR..." : "AI IS THINKING...";
    float textScale = 6.0f;
    float textWidth = strlen(thinkingText) * 8 * textScale;
    
    // Şık yarı saydam katman
    SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_BLEND);
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 120);
    SDL_FRect shadowRect = {0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT};
    SDL_RenderFillRect(renderer, &shadowRect);

    DrawText(renderer, fontTexture, thinkingText,
             LOGICAL_WIDTH / 2 - textWidth / 2,
             LOGICAL_HEIGHT / 2 - (8 * textScale) / 2, textScale,
             (SDL_Color){241, 196, 15, 255}); // Canlı Altın Rengi
  }

  // -- OYUN İÇİ BUTONLAR (2x Ölçekli) --
  // Ana Menü Butonu (Sol Alt)
  SDL_FRect menu_btn = {40, LOGICAL_HEIGHT - 120, 300, 80};
  SDL_SetRenderDrawColor(renderer, 127, 140, 141, 255); // Hoş Asfalt Grisi
  SDL_RenderFillRect(renderer, &menu_btn);
  
  const char *menu_txt = (game->language == 0) ? "ANA MENÜ" : "MAIN MENU";
  float menu_w = strlen(menu_txt) * 8 * 3.0f;
  DrawText(renderer, fontTexture, menu_txt, menu_btn.x + (menu_btn.w - menu_w) / 2, menu_btn.y + 24,
           3.0f, (SDL_Color){255, 255, 255, 255});

  // Replay Geri Düğmesi (<)
  SDL_FRect prev_btn = {600, LOGICAL_HEIGHT - 120, 160, 80};
  if (game->viewIndex > 0)
    SDL_SetRenderDrawColor(renderer, 230, 126, 34, 255); // Turuncu
  else
    SDL_SetRenderDrawColor(renderer, 189, 195, 199, 100); // Pasif
  SDL_RenderFillRect(renderer, &prev_btn);
  DrawText(renderer, fontTexture, "<", prev_btn.x + 70, prev_btn.y + 24, 3.0f,
           (SDL_Color){255, 255, 255, 255});

  // Replay İleri Düğmesi (>)
  SDL_FRect next_btn = {840, LOGICAL_HEIGHT - 120, 160, 80};
  if (game->viewIndex < game->historyCount)
    SDL_SetRenderDrawColor(renderer, 230, 126, 34, 255); // Turuncu
  else
    SDL_SetRenderDrawColor(renderer, 189, 195, 199, 100); // Pasif
  SDL_RenderFillRect(renderer, &next_btn);
  DrawText(renderer, fontTexture, ">", next_btn.x + 70, next_btn.y + 24, 3.0f,
           (SDL_Color){255, 255, 255, 255});

  // Tekrar Başlat Butonu (Sağ Alt)
  SDL_FRect restart_btn = {LOGICAL_WIDTH - 340, LOGICAL_HEIGHT - 120, 300, 80};
  SDL_SetRenderDrawColor(renderer, 41, 128, 185, 255); // Mavi
  SDL_RenderFillRect(renderer, &restart_btn);
  
  const char *restart_txt = (game->language == 0) ? "YENİDEN" : "RESTART";
  float restart_w = strlen(restart_txt) * 8 * 3.0f;
  DrawText(renderer, fontTexture, restart_txt, restart_btn.x + (restart_btn.w - restart_w) / 2,
           restart_btn.y + 24, 3.0f, (SDL_Color){255, 255, 255, 255});
}

static void DrawMainMenuScene(SDL_Renderer *renderer, SDL_Texture *fontTexture,
                               const Game *game) {
  // Premium Koyu Tema Degrade Arka Planı (Vertical Gradient)
  for (int y = 0; y < LOGICAL_HEIGHT; y += 4) {
    float ratio = (float)y / LOGICAL_HEIGHT;
    Uint8 r = (Uint8)(32 * (1.0f - ratio) + 18 * ratio);
    Uint8 g = (Uint8)(38 * (1.0f - ratio) + 20 * ratio);
    Uint8 b = (Uint8)(57 * (1.0f - ratio) + 30 * ratio);
    SDL_SetRenderDrawColor(renderer, r, g, b, 255);
    SDL_FRect lineRect = {0.0f, (float)y, (float)LOGICAL_WIDTH, 4.0f};
    SDL_RenderFillRect(renderer, &lineRect);
  }

  // --- Dil Secimi Butonu (Top-Right) ---
  SDL_FRect lang_btn = {LOGICAL_WIDTH - 260, 40, 220, 70};
  SDL_SetRenderDrawColor(renderer, 71, 89, 126, 255); // Yumuşak Lacivert
  SDL_RenderFillRect(renderer, &lang_btn);
  SDL_SetRenderDrawColor(renderer, 127, 143, 166, 255);
  SDL_RenderRect(renderer, &lang_btn);

  const char *lang_text = (game->language == 0) ? "DIL: TR" : "LANG: EN";
  float lang_textWidth = strlen(lang_text) * 8 * 3.0f;
  DrawText(renderer, fontTexture, lang_text,
           lang_btn.x + (lang_btn.w - lang_textWidth) / 2, lang_btn.y + 22, 3.0f,
           (SDL_Color){255, 255, 255, 255});

  // Başlık (8.0f Ölçekli, İnanılmaz Keskin)
  const char *title_text = (game->language == 0) ? "Türk Daması" : "Turkish Checkers";
  float title_w = strlen(title_text) * 8 * 8.0f;
  DrawText(renderer, fontTexture, title_text,
           LOGICAL_WIDTH / 2 - title_w / 2, 180, 8.0f,
           (SDL_Color){245, 246, 250, 255});

  // --- PVP Modu Butonu ---
  SDL_FRect pvp_btn = {LOGICAL_WIDTH / 2 - 300, 380, 600, 110};
  SDL_SetRenderDrawColor(renderer, 46, 204, 113, 255); // Canlı Zümrüt Yeşili
  SDL_RenderFillRect(renderer, &pvp_btn);
  
  if (!game->isPvE) {
    SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
    SDL_FRect border = {pvp_btn.x - 6, pvp_btn.y - 6, pvp_btn.w + 12, pvp_btn.h + 12};
    SDL_RenderRect(renderer, &border);
  }
  
  const char *pvp_text = (game->language == 0) ? "İki Kişilik" : "Two Players";
  float pvp_textWidth = strlen(pvp_text) * 8 * 4.0f;
  DrawText(renderer, fontTexture, pvp_text,
           LOGICAL_WIDTH / 2 - pvp_textWidth / 2, pvp_btn.y + 39, 4.0f,
           (SDL_Color){30, 30, 30, 255});

  // --- PVE Modu Butonu ---
  SDL_FRect pve_btn = {LOGICAL_WIDTH / 2 - 300, 510, 600, 110};
  SDL_SetRenderDrawColor(renderer, 230, 126, 34, 255); // Sıcak Turuncu/Bakır
  SDL_RenderFillRect(renderer, &pve_btn);
  
  if (game->isPvE) {
    SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
    SDL_FRect border = {pve_btn.x - 6, pve_btn.y - 6, pve_btn.w + 12, pve_btn.h + 12};
    SDL_RenderRect(renderer, &border);
  }

  const char *pve_text = (game->language == 0) ? "Bilgisayara Karşı" : "Play vs AI";
  float pve_textWidth = strlen(pve_text) * 8 * 4.0f;
  DrawText(renderer, fontTexture, pve_text,
           LOGICAL_WIDTH / 2 - pve_textWidth / 2, pve_btn.y + 39, 4.0f,
           (SDL_Color){30, 30, 30, 255});

  // --- PVE Ayrıntıları (AI Options Card Container) ---
  if (game->isPvE) {
    // Beautiful Modern Dark Slate Settings Box
    SDL_FRect options_card = {LOGICAL_WIDTH / 2 - 400, 660, 800, 440};
    SDL_SetRenderDrawColor(renderer, 28, 38, 57, 255); // Dark Slate background
    SDL_RenderFillRect(renderer, &options_card);
    SDL_SetRenderDrawColor(renderer, 71, 89, 126, 128); // Subtle borders
    SDL_RenderRect(renderer, &options_card);

    // Taraf Seçimi (Choose Side)
    const char *side_txt = (game->language == 0) ? "Taraf Seçimi" : "Choose Side";
    float side_w = strlen(side_txt) * 8 * 3.5f;
    DrawText(renderer, fontTexture, side_txt, LOGICAL_WIDTH / 2 - side_w / 2,
             690, 3.5f, (SDL_Color){220, 225, 230, 255});

    SDL_FRect white_btn = {LOGICAL_WIDTH / 2 - 210, 740, 200, 80};
    SDL_FRect black_btn = {LOGICAL_WIDTH / 2 + 10, 740, 200, 80};

    SDL_SetRenderDrawColor(renderer, 245, 245, 247, 255);
    SDL_RenderFillRect(renderer, &white_btn);

    SDL_SetRenderDrawColor(renderer, 30, 30, 30, 255);
    SDL_RenderFillRect(renderer, &black_btn);

    // Seçilen tarafı yeşil çerçeveyle vurguluyoruz
    if (game->aiPlayer == 2) {
      SDL_SetRenderDrawColor(renderer, 46, 204, 113, 255);
      SDL_FRect border = {white_btn.x - 4, white_btn.y - 4, white_btn.w + 8, white_btn.h + 8};
      SDL_RenderRect(renderer, &border);
    } else {
      SDL_SetRenderDrawColor(renderer, 46, 204, 113, 255);
      SDL_FRect border = {black_btn.x - 4, black_btn.y - 4, black_btn.w + 8, black_btn.h + 8};
      SDL_RenderRect(renderer, &border);
    }

    const char *white_txt = (game->language == 0) ? "Beyaz" : "White";
    float white_w = strlen(white_txt) * 8 * 3.0f;
    DrawText(renderer, fontTexture, white_txt, white_btn.x + (white_btn.w - white_w) / 2, white_btn.y + 24,
             3.0f, (SDL_Color){30, 30, 30, 255});

    const char *black_txt = (game->language == 0) ? "Siyah" : "Black";
    float black_w = strlen(black_txt) * 8 * 3.0f;
    DrawText(renderer, fontTexture, black_txt, black_btn.x + (black_btn.w - black_w) / 2, black_btn.y + 24,
             3.0f, (SDL_Color){255, 255, 255, 255});

    // Zorluk (Minimax Derinliği)
    const char *diff_txt = (game->language == 0) ? "Yapay Zeka Derinliği" : "AI Difficulty";
    float diff_w = strlen(diff_txt) * 8 * 3.5f;
    DrawText(renderer, fontTexture, diff_txt, LOGICAL_WIDTH / 2 - diff_w / 2, 
             870, 3.5f, (SDL_Color){220, 225, 230, 255});

    int depths[] = {4, 6, 8, 10, 12};
    int btnWidth = 100;
    int btnHeight = 80;
    int gap = 20;
    int totalWidth = (5 * btnWidth) + (4 * gap);
    int startX = (LOGICAL_WIDTH - totalWidth) / 2;
    int y = 920;

    for (int i = 0; i < 5; i++) {
      SDL_FRect btn = {startX + i * (btnWidth + gap), y, btnWidth, btnHeight};

      // Kolaydan zora: Yeşil -> Kırmızı
      if (i < 2)
        SDL_SetRenderDrawColor(renderer, 46, 204, 113, 200);
      else if (i < 4)
        SDL_SetRenderDrawColor(renderer, 241, 196, 15, 200);
      else
        SDL_SetRenderDrawColor(renderer, 231, 76, 60, 200);

      SDL_RenderFillRect(renderer, &btn);

      if (game->minimaxDepth == depths[i]) {
        SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
        SDL_FRect border = {btn.x - 4, btn.y - 4, btn.w + 8, btn.h + 8};
        SDL_RenderRect(renderer, &border);
      }

      char numStr[4];
      sprintf(numStr, "%d", depths[i]);
      DrawText(renderer, fontTexture, numStr, btn.x + 30, btn.y + 24, 3.0f,
               (SDL_Color){30, 30, 30, 255});
    }
  }

  // --- OYUNU BAŞLAT BUTONU ---
  float start_y = game->isPvE ? 1150.0f : 680.0f;
  SDL_FRect start_btn = {LOGICAL_WIDTH / 2 - 250, start_y, 500, 110};
  SDL_SetRenderDrawColor(renderer, 52, 152, 219, 255); // Premium Mavi
  SDL_RenderFillRect(renderer, &start_btn);
  
  const char *text = (game->language == 0) ? "OYUNU BAŞLAT" : "START GAME";
  float textWidth = strlen(text) * 8 * 4.0f;
  DrawText(renderer, fontTexture, text, LOGICAL_WIDTH / 2 - textWidth / 2,
           start_btn.y + 39, 4.0f, (SDL_Color){255, 255, 255, 255});
}

static void DrawGameOverScene(SDL_Renderer *renderer, SDL_Texture *fontTexture,
                               const Game *game) {
  // Oyun Sonu Karartma Katmanı
  SDL_SetRenderDrawColor(renderer, 44, 62, 80, 255);
  SDL_RenderClear(renderer);
  
  char text[100];
  if (game->language == 0) {
    if (game->winner == 3) {
      sprintf(text, "Oyun Bitti! Beraberlik (Gayyım)");
    } else {
      sprintf(text, "Oyun Bitti! Kazanan: %s",
              (game->winner == 1) ? "Beyaz" : "Siyah");
    }
  } else {
    if (game->winner == 3) {
      sprintf(text, "Game Over! Draw (Gayyım)");
    } else {
      sprintf(text, "Game Over! Winner: %s",
              (game->winner == 1) ? "White" : "Black");
    }
  }
  
  float textWidth = strlen(text) * 8 * 4.0f;
  DrawText(renderer, fontTexture, text, LOGICAL_WIDTH / 2 - textWidth / 2,
           LOGICAL_HEIGHT / 2 - 16, 4.0f, (SDL_Color){245, 246, 250, 255});

  // Alt bilgi (Herhangi bir yere tıkla çıkışı için)
  const char *info = (game->language == 0) ? "Ana menüye dönmek için herhangi bir yere tıklayın." : "Click anywhere to return to main menu.";
  float info_w = strlen(info) * 8 * 2.0f;
  DrawText(renderer, fontTexture, info, LOGICAL_WIDTH / 2 - info_w / 2,
           LOGICAL_HEIGHT / 2 + 100, 2.0f, (SDL_Color){189, 195, 199, 255});
}
