// DamaC/include/dama_game.h
#ifndef DAMA_GAME_H
#define DAMA_GAME_H

#include "dama_config.h"
#include <stdbool.h>

// --- Veri Yapıları ve Numaralandırmalar ---

// Oyunun farklı durumlarını temsil eder.
typedef enum { STATE_MAIN_MENU, STATE_IN_GAME, STATE_GAME_OVER } GameState;

// Tahtadaki karelerin durumunu temsil eder.
typedef enum {
  BOS_KARE = 0,
  BEYAZ_TAS = 1,
  SIYAH_TAS = 2,
  BEYAZ_DAMA = 3,
  SIYAH_DAMA = 4
} TasTipi;

// Tahtadaki bir koordinatı (satır, sütun) temsil eder.
typedef struct {
  int row;
  int col;
} Koordinat;

// Bir hamleyi (nereden, nereye) temsil eder.
typedef struct {
  Koordinat from;
  Koordinat to;
} Hamle;

// Oyuncuların puanlarını tutmak için yapı.
typedef struct {
  int white;
  int black;
} Scores;

// Hamle geçmişini tutmak için yapı
typedef struct {
  TasTipi board[BOARD_SIZE][BOARD_SIZE];
  char notation[20]; // Örn: "a3-b4"
  int activePlayer;
} HistoryState;

#define MAX_MOVES 500

// Oyunun tüm anlık durumunu içeren ana yapı.
typedef struct {
  TasTipi board[BOARD_SIZE][BOARD_SIZE];
  int currentPlayer; // 1: Beyaz, 2: Siyah
  Koordinat selectedPiece;
  Hamle possibleMoves[256];
  int moveCount;
  int winner; // 0: Yok, 1: Beyaz, 2: Siyah
  bool isCaptureMandatory;
  Hamle lastMove;
  GameState currentState;
  Scores scores;

  // AI Settings
  bool isPvE;       // PvE modu açık mı?
  int aiPlayer;     // AI hangi oyuncu? (Genelde 2: Siyah)
  int minimaxDepth; // AI Zorluk Seviyesi

  // History & Replay
  HistoryState history[MAX_MOVES];
  int historyCount; // Toplam hamle sayısı
  int viewIndex;    // Şu an görüntülenen hamle indisi

  int language;     // 0: Türkçe, 1: English
} Game;

// --- Fonksiyon Protototipleri ---

/**
 * @brief Yeni bir oyun nesnesi oluşturur ve bellekte yer ayırır.
 * @return Oluşturulan Game nesnesinin işaretçisi.
 */
Game *Game_Create();

/**
 * @brief Oluşturulan oyun nesnesini ve ayrılan belleği serbest bırakır.
 * @param game Yok edilecek oyun nesnesi.
 */
void Game_Destroy(Game *game);

/**
 * @brief Oyunu başlangıç durumuna getirir (Ana Menü).
 * @param game Sıfırlanacak oyun nesnesi.
 */
void Game_Reset(Game *game);

/**
 * @brief Oyunu başlatır, tahtayı kurar ve ilk hamleleri hesaplar.
 * @param game Başlatılacak oyun nesnesi.
 */
void Game_Start(Game *game);

/**
 * @brief Ekrana yapılan bir tıklamayı işler.
 * Ana menüde butona tıklama veya oyun sırasında tahtaya tıklama.
 * @param game İşlemin yapılacağı oyun nesnesi.
 * @param mouseX Farenin x koordinatı.
 * @param mouseY Farenin y koordinatı.
 */
void Game_HandleClick(Game *game, int mouseX, int mouseY);

// --- AI Entegrasyonu için API ---

/**
 * @brief Verilen bir tahta üzerinde belirtilen hamleyi simüle eder.
 * @param board Üzerinde işlem yapılacak tahta (Game'den bağımsız olabilir).
 * @param from Hamle başlangıç.
 * @param to Hamle bitiş.
 * @param isCaptureMandatory Zorunlu yeme durumu var mıydı?
 * @return Eğer hamle sonucunda tekrar hamle hakkı doğarsa (zincirleme yeme)
 * true döner.
 */
bool Game_SimulateMove(TasTipi board[BOARD_SIZE][BOARD_SIZE], Koordinat from,
                       Koordinat to, bool isCaptureMandatory);

/**
 * @brief Verilen bir tahta durumu için oyuncunun olası hamlelerini hesaplar.
 * @param board Analiz edilecek tahta.
 * @param player Hamle sırası kimde (1 veya 2).
 * @param moves Bulunan hamlelerin yazılacağı dizi.
 * @param count Bulunan hamle sayısı (output).
 * @param isCaptureMandatory Zorunlu yeme var mı (output).
 */
void Game_FindAllPossibleMovesForBoard(TasTipi board[BOARD_SIZE][BOARD_SIZE],
                                       int player, Hamle moves[], int *count,
                                       bool *isCaptureMandatory);

/**
 * @brief Belirtilen hamleyi gerçek oyun tahtasına uygular.
 * @param game Oyun nesnesi.
 * @param from Hamle başlangıç.
 * @param to Hamle bitiş.
 */
void Game_MakeMove(Game *game, Koordinat from, Koordinat to);

/**
 * @brief Kilitli taş için hamleleri bulur (AI zincirleme yeme için).
 */
void Game_FindMovesForLockedPiece(TasTipi board[BOARD_SIZE][BOARD_SIZE],
                                  int player, Koordinat lockedPiece,
                                  Hamle moves[], int *count);

/**
 * @brief Ana menüdeki tıklamaları işler.
 */
void Game_HandleMenuClick(Game *game, int x, int y);

#endif // DAMA_GAME_H
