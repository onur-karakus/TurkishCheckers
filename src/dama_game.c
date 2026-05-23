// DamaC/src/dama_game.c

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "dama_game.h"

// --- Dahili Fonksiyon Prototipleri (Bu dosyaya özel) ---
static void logMessage(const char *prefix, const char *message);
static bool isOpponent(TasTipi piece, int player);
static bool isOnBoard(Koordinat k);
static void findAllPossibleMoves(Game *game);
static int calculateMaxCaptureLength(TasTipi board[8][8], Koordinat from,
                                     int lastMoveDir);
static void Game_UpdateScores(Game *game); // GÜNCELLEME: Puan hesaplama fonksiyonu prototipi

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

// GÜNCELLEME: Tahtadaki taşları sayarak puanları güncelleyen yeni fonksiyon
static void Game_UpdateScores(Game *game) {
  logMessage("[GAME]", "Puanlar yeniden hesaplanıyor...");
  game->scores.white = 0;
  game->scores.black = 0;

  int whiteCount = 0;
  int blackCount = 0;

  for (int r = 0; r < BOARD_SIZE; r++) {
    for (int c = 0; c < BOARD_SIZE; c++) {
      switch (game->board[r][c]) {
      case BEYAZ_TAS:
        game->scores.white += 1;
        whiteCount++;
        break;
      case BEYAZ_DAMA:
        game->scores.white += 5;
        whiteCount++;
        break;
      case SIYAH_TAS:
        game->scores.black += 1;
        blackCount++;
        break;
      case SIYAH_DAMA:
        game->scores.black += 5;
        blackCount++;
        break;
      default:
        break; // BOS_KARE için bir şey yapma
      }
    }
  }
  char scoreLog[128];
  sprintf(scoreLog, "Hesaplanan Puanlar -> Beyaz: %d, Siyah: %d | Taş Sayıları -> Beyaz: %d, Siyah: %d",
          game->scores.white, game->scores.black, whiteCount, blackCount);
  logMessage("[GAME]", scoreLog);

  // GAYYIM KURALI: Her iki tarafın da tam 1 taşı kalmışsa beraberlik
  if (game->currentState == STATE_IN_GAME && whiteCount == 1 && blackCount == 1) {
    logMessage("[GAME]", "Oyun bitti! Her iki tarafın da tek taşı kaldı (Gayyım Beraberliği).");
    game->currentState = STATE_GAME_OVER;
    game->winner = 3; // 3: Draw (Gayyım)
  }
}

// --- Harici (Public) Fonksiyonlar ---

Game *Game_Create() {
  logMessage("[GAME]", "Game nesnesi için bellek ayrılıyor...");
  Game *game = (Game *)malloc(sizeof(Game));
  if (game == NULL) {
    logMessage("[GAME]", "HATA: Game nesnesi için bellek ayrılamadı!");
    return NULL;
  }
  logMessage("[GAME]", "Game nesnesi başarıyla oluşturuldu.");
  Game_Reset(game);
  game->language = 1; // Varsayılan olarak İngilizce (1)
  return game;
}

void Game_Destroy(Game *game) {
  if (game != NULL) {
    logMessage("[GAME]", "Game nesnesi bellekten siliniyor.");
    free(game);
  }
}

void Game_Reset(Game *game) {
  logMessage("[GAME]", "Oyun baslangic durumuna (Ana Menu) getiriliyor...");
  game->currentState = STATE_MAIN_MENU;
  game->isPvE = true; // Varsayilan olarak PVE acik olsun
  game->aiPlayer = 2; // AI Siyah oynasin
  game->minimaxDepth = 6; // Varsayilan Orta (6)
  game->scores.white = 0;
  game->scores.black = 0;
}

void Game_Start(Game *game) {
  logMessage("[GAME]", "Yeni oyun başlatılıyor ve tahta kuruluyor...");
  game->currentState = STATE_IN_GAME;
  for (int i = 0; i < BOARD_SIZE; i++) {
    for (int j = 0; j < BOARD_SIZE; j++) {
      if (i == 1 || i == 2)
        game->board[i][j] = SIYAH_TAS;
      else if (i == 5 || i == 6)
        game->board[i][j] = BEYAZ_TAS;
      else
        game->board[i][j] = BOS_KARE;
    }
  }
  game->currentPlayer = 1; // Beyaz baslar
  game->winner = 0;
  game->selectedPiece = (Koordinat){-1, -1};
  game->lastMove = (Hamle){{-1, -1}, {-1, -1}};

  // GÜNCELLEME: Başlangıç puanlarını ve hamleleri hesapla
  Game_UpdateScores(game);
  findAllPossibleMoves(game);

  // History Init
  game->historyCount = 0;
  for (int i = 0; i < 8; i++) {
    for (int j = 0; j < 8; j++) {
      game->history[0].board[i][j] = game->board[i][j];
    }
  }
  strcpy(game->history[0].notation, "Start");
  game->history[0].activePlayer = 0;
  game->viewIndex = 0;

  logMessage("[GAME]", "Oyun başlatıldı. Sıra Beyaz oyuncuda.");
}

// --- Yardımcı Mantık Fonksiyonları (Dahili) ---

static void GenerateNotation(Koordinat from, Koordinat to, bool isCapture,
                              char *buffer) {
  char cols[] = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'};
  char rows[] = {'1', '2', '3', '4', '5', '6', '7', '8'};
  if (isCapture) {
    sprintf(buffer, "%c%c x %c%c", cols[from.col], rows[from.row], cols[to.col],
            rows[to.row]);
  } else {
    sprintf(buffer, "%c%c-%c%c", cols[from.col], rows[from.row], cols[to.col],
            rows[to.row]);
  }
}

static void SaveHistory(Game *game, Koordinat from, Koordinat to,
                         bool isCapture) {
  if (game->historyCount >= MAX_MOVES - 1)
    return;

  game->historyCount++;
  // Tahtayı kopyala
  for (int i = 0; i < 8; i++) {
    for (int j = 0; j < 8; j++) {
      game->history[game->historyCount].board[i][j] = game->board[i][j];
    }
  }
  // Notasyonu kaydet
  GenerateNotation(from, to, isCapture,
                   game->history[game->historyCount].notation);

  // Aktif oyuncuyu kaydet (Hamleyi yapan)
  game->history[game->historyCount].activePlayer = game->currentPlayer;

  // View index'i son hamleye getir
  game->viewIndex = game->historyCount;
}

static bool isOpponent(TasTipi piece, int player) {
  if (player == 1) // Beyaz oyuncu
    return (piece == SIYAH_TAS || piece == SIYAH_DAMA);
  else // Siyah oyuncu
    return (piece == BEYAZ_TAS || piece == BEYAZ_DAMA);
}

static bool isOnBoard(Koordinat k) {
  return k.row >= 0 && k.row < 8 && k.col >= 0 && k.col < 8;
}

// --- Hamle Hesaplama Fonksiyonları (Dahili) ---

static void findMovesForPiece(TasTipi board[8][8], int player, Koordinat from,
                               Hamle moves[], int *count) {
  int dr[] = {0, 0, 1, -1}; // Sağ, Sol, İleri(Siyah), İleri(Beyaz)
  int dc[] = {1, -1, 0, 0};

  for (int i = 0; i < 4; i++) {
    Koordinat to = {from.row + dr[i], from.col + dc[i]};

    if (player == 1 && dr[i] > 0)
      continue;
    if (player == 2 && dr[i] < 0)
      continue;
    if (player == 1 && to.row > from.row)
      continue;
    if (player == 2 && to.row < from.row)
      continue;

    if (isOnBoard(to) && board[to.row][to.col] == BOS_KARE) {
      moves[*count] = (Hamle){from, to};
      (*count)++;
    }
  }
}

static void findMovesForDama(TasTipi board[8][8], Koordinat from, Hamle moves[],
                             int *count) {
  int dr[] = {-1, 1, 0, 0}; // Yukarı, Aşağı, Sol, Sağ
  int dc[] = {0, 0, -1, 1};
  for (int i = 0; i < 4; i++) {
    for (int k = 1; k < 8; k++) {
      Koordinat to = {from.row + k * dr[i], from.col + k * dc[i]};
      if (isOnBoard(to)) {
        if (board[to.row][to.col] == BOS_KARE) {
          moves[*count] = (Hamle){from, to};
          (*count)++;
        } else
          break;
      } else
        break;
    }
  }
}

static void findCapturesForPiece(TasTipi board[8][8], int player,
                                 Koordinat from, Hamle captures[], int *count) {
  int dr[] = {0, 0, 2, -2};
  int dc[] = {2, -2, 0, 0};

  for (int i = 0; i < 4; i++) {
    Koordinat to = {from.row + dr[i], from.col + dc[i]};
    Koordinat captured = {from.row + dr[i] / 2, from.col + dc[i] / 2};
    if (isOnBoard(to) && board[to.row][to.col] == BOS_KARE) {
      if (isOnBoard(captured) &&
          isOpponent(board[captured.row][captured.col], player)) {
        captures[*count] = (Hamle){from, to};
        (*count)++;
      }
    }
  }
}

static bool hasYozCaptures(TasTipi board[8][8], int player, Koordinat pos) {
  Hamle tempCaptures[64];
  int tempCount = 0;
  findCapturesForPiece(board, player, pos, tempCaptures, &tempCount);
  return tempCount > 0;
}

static void findCapturesForDama(TasTipi board[8][8], int player, Koordinat from,
                                Hamle captures[], int *count) {
  int dr[] = {-1, 1, 0, 0};
  int dc[] = {0, 0, -1, 1};

  for (int i = 0; i < 4; i++) {
    Koordinat opponentPos = {-1, -1};
    int opponentCount = 0;
    for (int k = 1; k < 8; k++) {
      Koordinat current = {from.row + k * dr[i], from.col + k * dc[i]};
      if (!isOnBoard(current))
        break;

      TasTipi pieceOnSquare = board[current.row][current.col];
      if (pieceOnSquare != BOS_KARE) {
        if (isOpponent(pieceOnSquare, player)) {
          opponentCount++;
          opponentPos = current;
        } else
          break;
      } else {
        if (opponentCount == 1) {
          captures[*count] = (Hamle){from, current};
          (*count)++;
        }
      }
      if (opponentCount > 1)
        break;
    }
  }
}

static int calculateMaxCaptureLength(TasTipi tempBoard[8][8], Koordinat from,
                                     int lastMoveDir) {
  int maxLen = 0;
  TasTipi piece = tempBoard[from.row][from.col];
  if (piece == BOS_KARE)
    return 0;

  bool isDama = (piece == BEYAZ_DAMA || piece == SIYAH_DAMA);
  int player = (piece == BEYAZ_TAS || piece == BEYAZ_DAMA) ? 1 : 2;

  int dr[] = {-1, 1, 0, 0};
  int dc[] = {0, 0, -1, 1};

  for (int i = 0; i < 4; i++) {
    if (lastMoveDir != -1 && abs(lastMoveDir - i) == 1 &&
        (lastMoveDir / 2 == i / 2))
      continue;

    if (isDama) {
      Koordinat opponentPos = {-1, -1};
      int opponentCount = 0;
      for (int k = 1; k < 8; k++) {
        Koordinat currentPos = {from.row + k * dr[i], from.col + k * dc[i]};
        if (!isOnBoard(currentPos))
          break;

        TasTipi pieceOnSquare = tempBoard[currentPos.row][currentPos.col];
        if (pieceOnSquare != BOS_KARE) {
          if (isOpponent(pieceOnSquare, player)) {
            opponentCount++;
            opponentPos = currentPos;
          } else
            break;
        } else {
          if (opponentCount == 1) {
            TasTipi nextBoard[8][8];
            memcpy(nextBoard, tempBoard, sizeof(TasTipi) * 64);
            nextBoard[currentPos.row][currentPos.col] = piece;
            nextBoard[from.row][from.col] = BOS_KARE;
            nextBoard[opponentPos.row][opponentPos.col] = BOS_KARE;
            int len = 1 + calculateMaxCaptureLength(nextBoard, currentPos, i);
            if (len > maxLen)
              maxLen = len;
          }
        }
        if (opponentCount > 1)
          break;
      }
    } else { // Normal taş
      if (player == 1 && dr[i] > 0 && i < 2)
        continue;
      if (player == 2 && dr[i] < 0 && i < 2)
        continue;

      Koordinat opponentPos = {from.row + dr[i], from.col + dc[i]};
      Koordinat landingPos = {from.row + 2 * dr[i], from.col + 2 * dc[i]};

      if (isOnBoard(landingPos) &&
          tempBoard[landingPos.row][landingPos.col] == BOS_KARE) {
        if (isOnBoard(opponentPos) &&
            isOpponent(tempBoard[opponentPos.row][opponentPos.col], player)) {
          TasTipi nextBoard[8][8];
          memcpy(nextBoard, tempBoard, sizeof(TasTipi) * 64);
          nextBoard[landingPos.row][landingPos.col] = piece;
          nextBoard[from.row][from.col] = BOS_KARE;
          nextBoard[opponentPos.row][opponentPos.col] = BOS_KARE;
          int len = 1 + calculateMaxCaptureLength(nextBoard, landingPos, i);
          if (len > maxLen)
            maxLen = len;
        }
      }
    }
  }
  return maxLen;
}

// Yardımcı: Bir hamlenin sonucunda kalan maksimum yeme uzunluğunu hesaplar
static int getCaptureLengthForMove(TasTipi board[8][8], Hamle move) {
  TasTipi tempBoard[8][8];
  memcpy(tempBoard, board, sizeof(TasTipi) * 64);

  // Hamleyi uygula (Simülasyon - Basitleştirilmiş)
  TasTipi piece = tempBoard[move.from.row][move.from.col];
  tempBoard[move.to.row][move.to.col] = piece;
  tempBoard[move.from.row][move.from.col] = BOS_KARE;

  // Yenen taşı kaldır
  int r_diff = move.to.row - move.from.row;
  int c_diff = move.to.col - move.from.col;

  if (piece == BEYAZ_DAMA || piece == SIYAH_DAMA) {
    int r_step = (r_diff > 0) ? 1 : ((r_diff < 0) ? -1 : 0);
    int c_step = (c_diff > 0) ? 1 : ((c_diff < 0) ? -1 : 0);
    for (int i = 1;; i++) {
      Koordinat current = {move.from.row + i * r_step,
                           move.from.col + i * c_step};
      if (current.row == move.to.row && current.col == move.to.col)
        break;
      if (tempBoard[current.row][current.col] != BOS_KARE) {
        tempBoard[current.row][current.col] = BOS_KARE; // Yendi
        break;
      }
    }
  } else {
    tempBoard[(move.from.row + move.to.row) / 2]
             [(move.from.col + move.to.col) / 2] = BOS_KARE;
  }

  int dirIndex = -1;
  if (r_diff < 0 && c_diff == 0)
    dirIndex = 0; // Yukarı
  else if (r_diff > 0 && c_diff == 0)
    dirIndex = 1; // Aşağı
  else if (r_diff == 0 && c_diff < 0)
    dirIndex = 2; // Sol
  else if (r_diff == 0 && c_diff > 0)
    dirIndex = 3; // Sağ

  return 1 + calculateMaxCaptureLength(tempBoard, move.to, dirIndex);
}

void Game_FindAllPossibleMovesForBoard(TasTipi board[BOARD_SIZE][BOARD_SIZE],
                                       int player, Hamle moves[], int *count,
                                       bool *isCaptureMandatory) {
  *count = 0;
  int maxCaptureOverall = 0;

  // 1. En uzun yeme zincirini bul
  for (int r = 0; r < 8; r++) {
    for (int c = 0; c < 8; c++) {
      TasTipi piece = board[r][c];
      if ((player == 1 && (piece == BEYAZ_TAS || piece == BEYAZ_DAMA)) ||
          (player == 2 && (piece == SIYAH_TAS || piece == SIYAH_DAMA))) {
        int len = calculateMaxCaptureLength(board, (Koordinat){r, c}, -1);
        if (len > maxCaptureOverall)
          maxCaptureOverall = len;
      }
    }
  }

  if (maxCaptureOverall > 0) {
    *isCaptureMandatory = true;
    for (int r = 0; r < 8; r++) {
      for (int c = 0; c < 8; c++) {
        TasTipi piece = board[r][c];
        if ((player == 1 && (piece == BEYAZ_TAS || piece == BEYAZ_DAMA)) ||
            (player == 2 && (piece == SIYAH_TAS || piece == SIYAH_DAMA))) {

          // Sadece bu parça potansiyel olarak maks uzunluğa ulaşabiliyorsa adayları al
          if (calculateMaxCaptureLength(board, (Koordinat){r, c}, -1) ==
              maxCaptureOverall) {

            int candidateCount = 0;
            Hamle candidates[64];

            if (piece == BEYAZ_DAMA || piece == SIYAH_DAMA)
              findCapturesForDama(board, player, (Koordinat){r, c}, candidates,
                                  &candidateCount);
            else
              findCapturesForPiece(board, player, (Koordinat){r, c}, candidates,
                                   &candidateCount);

            // Aday hamleleri filtrele: Sadece maxCaptureOverall'a ulaştıran zincirin ilk adımını kabul et
            for (int i = 0; i < candidateCount; i++) {
              int totalLen = getCaptureLengthForMove(board, candidates[i]);
              if (totalLen == maxCaptureOverall) {
                moves[*count] = candidates[i];
                (*count)++;
              }
            }
          }
        }
      }
    }
  } else {
    *isCaptureMandatory = false;
    for (int r = 0; r < 8; r++) {
      for (int c = 0; c < 8; c++) {
        TasTipi piece = board[r][c];
        if ((player == 1 && (piece == BEYAZ_TAS || piece == BEYAZ_DAMA)) ||
            (player == 2 && (piece == SIYAH_TAS || piece == SIYAH_DAMA))) {
          if (piece == BEYAZ_DAMA || piece == SIYAH_DAMA)
            findMovesForDama(board, (Koordinat){r, c}, moves, count);
          else
            findMovesForPiece(board, player, (Koordinat){r, c}, moves, count);
        }
      }
    }
  }
}

// AI için kilitli taş hamle bulucu
void Game_FindMovesForLockedPiece(TasTipi board[8][8], int player,
                                  Koordinat lockedPiece, Hamle moves[],
                                  int *count) {
  *count = 0;
  TasTipi piece = board[lockedPiece.row][lockedPiece.col];

  if (piece == BOS_KARE)
    return;
  if (player == 1 && !(piece == BEYAZ_TAS || piece == BEYAZ_DAMA))
    return;
  if (player == 2 && !(piece == SIYAH_TAS || piece == SIYAH_DAMA))
    return;

  int maxLen = calculateMaxCaptureLength(board, lockedPiece, -1);

  if (maxLen > 0) {
    int candidateCount = 0;
    Hamle candidates[64];

    if (piece == BEYAZ_DAMA || piece == SIYAH_DAMA)
      findCapturesForDama(board, player, lockedPiece, candidates,
                          &candidateCount);
    else
      findCapturesForPiece(board, player, lockedPiece, candidates,
                           &candidateCount);

    for (int i = 0; i < candidateCount; i++) {
      int moveLen = getCaptureLengthForMove(board, candidates[i]);
      if (moveLen == maxLen) {
        moves[*count] = candidates[i];
        (*count)++;
      }
    }
  } else {
    if (piece == BEYAZ_DAMA || piece == SIYAH_DAMA)
      findMovesForDama(board, lockedPiece, moves, count);
    else
      findMovesForPiece(board, player, lockedPiece, moves, count);
  }
}

static void findAllPossibleMoves(Game *game) {
  char log[128];
  sprintf(log, "Oyuncu %d icin olasi hamleler hesaplaniyor...",
          game->currentPlayer);
  logMessage("[GAME]", log);

  Game_FindAllPossibleMovesForBoard(game->board, game->currentPlayer,
                                    game->possibleMoves, &game->moveCount,
                                    &game->isCaptureMandatory);

  sprintf(log,
          "Toplam %d adet gecerli baslangic hamlesi bulundu. Zorunlu yeme: %d",
          game->moveCount, game->isCaptureMandatory);
  logMessage("[GAME]", log);
}

bool Game_SimulateMove(TasTipi board[BOARD_SIZE][BOARD_SIZE], Koordinat from,
                       Koordinat to, bool isCaptureMandatory) {
  TasTipi movingPiece = board[from.row][from.col];

  if (isCaptureMandatory) {
    Koordinat capturedPos = {-1, -1};
    if (movingPiece == BEYAZ_DAMA || movingPiece == SIYAH_DAMA) {
      int r_step = (to.row > from.row) ? 1 : ((to.row < from.row) ? -1 : 0);
      int c_step = (to.col > from.col) ? 1 : ((to.col < from.col) ? -1 : 0);
      for (int i = 1;; i++) {
        Koordinat current = {from.row + i * r_step, from.col + i * c_step};
        if (current.row == to.row && current.col == to.col)
          break;
        if (board[current.row][current.col] != BOS_KARE) {
          capturedPos = current;
          break;
        }
      }
    } else {
      capturedPos =
          (Koordinat){(from.row + to.row) / 2, (from.col + to.col) / 2};
    }
    if (capturedPos.row != -1 && isOnBoard(capturedPos)) {
      board[capturedPos.row][capturedPos.col] = BOS_KARE;
    }
  }

  board[to.row][to.col] = movingPiece;
  board[from.row][from.col] = BOS_KARE;

  bool justPromoted = false;
  int player = (movingPiece == BEYAZ_TAS || movingPiece == BEYAZ_DAMA) ? 1 : 2;
  if (board[to.row][to.col] == BEYAZ_TAS && to.row == 0) {
    if (isCaptureMandatory && hasYozCaptures(board, player, to)) {
      justPromoted = false;
    } else {
      board[to.row][to.col] = BEYAZ_DAMA;
      justPromoted = true;
    }
  }
  if (board[to.row][to.col] == SIYAH_TAS && to.row == 7) {
    if (isCaptureMandatory && hasYozCaptures(board, player, to)) {
      justPromoted = false;
    } else {
      board[to.row][to.col] = SIYAH_DAMA;
      justPromoted = true;
    }
  }

  if (isCaptureMandatory && !justPromoted) {
    int len = calculateMaxCaptureLength(board, to, -1);
    if (len > 0)
      return true; // Zincirleme devam ediyor
  }

  return false;
}

void Game_MakeMove(Game *game, Koordinat from, Koordinat to) {
  char log[100];
  sprintf(log, "Hamle yapılıyor: (%d,%d) -> (%d,%d)", from.row, from.col,
          to.row, to.col);
  logMessage("[GAME]", log);

  game->lastMove = (Hamle){from, to};
  TasTipi movingPiece = game->board[from.row][from.col];

  if (game->isCaptureMandatory) {
    logMessage("[GAME]", "Bu bir yeme hamlesi.");
    Koordinat capturedPos = {-1, -1};
    if (movingPiece == BEYAZ_DAMA || movingPiece == SIYAH_DAMA) {
      int r_step = (to.row > from.row) ? 1 : ((to.row < from.row) ? -1 : 0);
      int c_step = (to.col > from.col) ? 1 : ((to.col < from.col) ? -1 : 0);
      for (int i = 1;; i++) {
        Koordinat current = {from.row + i * r_step, from.col + i * c_step};
        if (game->board[current.row][current.col] != BOS_KARE) {
          capturedPos = current;
          break;
        }
        if (current.row == to.row && current.col == to.col)
          break;
      }
    } else {
      capturedPos =
          (Koordinat){(from.row + to.row) / 2, (from.col + to.col) / 2};
    }
    if (capturedPos.row != -1) {
      sprintf(log, "Taş yendi: (%d,%d)", capturedPos.row, capturedPos.col);
      logMessage("[GAME]", log);
      game->board[capturedPos.row][capturedPos.col] = BOS_KARE;
    }
  }

  game->board[to.row][to.col] = game->board[from.row][from.col];
  game->board[from.row][from.col] = BOS_KARE;

  bool justPromoted = false;
  int player = (movingPiece == BEYAZ_TAS || movingPiece == BEYAZ_DAMA) ? 1 : 2;
  if (game->board[to.row][to.col] == BEYAZ_TAS && to.row == 0) {
    if (game->isCaptureMandatory && hasYozCaptures(game->board, player, to)) {
      justPromoted = false;
      logMessage("[GAME]", "Beyaz taş son sıraya ulaştı ama yemeğe devam ettiği için henüz Dama olmadı!");
    } else {
      game->board[to.row][to.col] = BEYAZ_DAMA;
      justPromoted = true;
      logMessage("[GAME]", "Beyaz taş Dama oldu!");
    }
  }
  if (game->board[to.row][to.col] == SIYAH_TAS && to.row == 7) {
    if (game->isCaptureMandatory && hasYozCaptures(game->board, player, to)) {
      justPromoted = false;
      logMessage("[GAME]", "Siyah taş son sıraya ulaştı ama yemeğe devam ettiği için henüz Dama olmadı!");
    } else {
      game->board[to.row][to.col] = SIYAH_DAMA;
      justPromoted = true;
      logMessage("[GAME]", "Siyah taş Dama oldu!");
    }
  }

  bool isCapture = (game->isCaptureMandatory && !justPromoted);
  SaveHistory(game, from, to, isCapture);

  if (game->isCaptureMandatory && !justPromoted) {
    logMessage("[GAME]",
               "Çoklu yeme ihtimali için hamleler yeniden hesaplanıyor...");
    findAllPossibleMoves(game);
    if (game->isCaptureMandatory) {
      int continuedMoveCount = 0;
      Hamle continuedMoves[256];

      for (int i = 0; i < game->moveCount; i++) {
        if (game->possibleMoves[i].from.row == to.row &&
            game->possibleMoves[i].from.col == to.col) {
          continuedMoves[continuedMoveCount++] = game->possibleMoves[i];
        }
      }

      if (continuedMoveCount > 0) {
        logMessage("[GAME]", "Zincirleme hamle bulundu. Diğer taşların hamleleri iptal ediliyor.");

        game->moveCount = continuedMoveCount;
        for (int k = 0; k < continuedMoveCount; k++) {
          game->possibleMoves[k] = continuedMoves[k];
        }

        game->selectedPiece = to;
        Game_UpdateScores(game);
        return;
      }
    }
  }

  game->currentPlayer = (game->currentPlayer == 1) ? 2 : 1;
  sprintf(log, "Sıra oyuncu %d'e geçti.", game->currentPlayer);
  logMessage("[GAME]", log);
  game->selectedPiece = (Koordinat){-1, -1};

  Game_UpdateScores(game);
  findAllPossibleMoves(game);
}

void Game_HandleClick(Game *game, int mouseX, int mouseY) {
  char log[100];

  // --- OYUN İÇİ BUTONLAR (Mantıksal koordinatlar üzerinden, 2x Ölçekli) ---
  // Ana Menü Butonu: {40, LOGICAL_HEIGHT - 120, 300, 80}
  // x: [40, 340], y: [LOGICAL_HEIGHT - 120, LOGICAL_HEIGHT - 40]
  if (mouseX >= 40 && mouseX <= 340 && mouseY >= LOGICAL_HEIGHT - 120 &&
      mouseY <= LOGICAL_HEIGHT - 40) {
    logMessage("[GAME]", "Ana Menü butonuna tıklandı.");
    Game_Reset(game);
    return;
  }

  // Tekrar Başlat Butonu: {LOGICAL_WIDTH - 340, LOGICAL_HEIGHT - 120, 300, 80}
  // x: [LOGICAL_WIDTH - 340, LOGICAL_WIDTH - 40], y: [LOGICAL_HEIGHT - 120, LOGICAL_HEIGHT - 40]
  if (mouseX >= LOGICAL_WIDTH - 340 && mouseX <= LOGICAL_WIDTH - 40 &&
      mouseY >= LOGICAL_HEIGHT - 120 && mouseY <= LOGICAL_HEIGHT - 40) {
    logMessage("[GAME]", "Tekrar Başlat butonuna tıklandı.");
    Game_Start(game);
    return;
  }

  // Replay Butonları (Orta Alt)
  // Geri (<): {600, LOGICAL_HEIGHT - 120, 160, 80}
  if (mouseX >= 600 && mouseX <= 760 && mouseY >= LOGICAL_HEIGHT - 120 &&
      mouseY <= LOGICAL_HEIGHT - 40) {
    if (game->viewIndex > 0) {
      game->viewIndex--;
      logMessage("[GAME]", "Replay: Geri gelindi.");
    }
    return;
  }

  // İleri (>): {840, LOGICAL_HEIGHT - 120, 160, 80}
  if (mouseX >= 840 && mouseX <= 1000 && mouseY >= LOGICAL_HEIGHT - 120 &&
      mouseY <= LOGICAL_HEIGHT - 40) {
    if (game->viewIndex < game->historyCount) {
      game->viewIndex++;
      logMessage("[GAME]", "Replay: İleri gidildi.");
    }
    return;
  }

  if (mouseX < BOARD_OFFSET || mouseX > BOARD_OFFSET + BOARD_AREA_SIZE ||
      mouseY < BOARD_OFFSET || mouseY > BOARD_OFFSET + BOARD_AREA_SIZE) {
    logMessage("[GAME]", "Tahta dışına tıklandı, seçim iptal ediliyor.");
    game->selectedPiece = (Koordinat){-1, -1};
    return;
  }

  // Replay Modunda Islem Engelleme
  if (game->viewIndex != game->historyCount) {
    logMessage("[GAME]", "Geçmiş izleniyor. Hamle yapılamaz.");
    return;
  }

  Koordinat clicked = {(int)((mouseY - BOARD_OFFSET) / SQUARE_SIZE),
                       (int)((mouseX - BOARD_OFFSET) / SQUARE_SIZE)};
  sprintf(log, "Oyun tahtasında kareye tıklandı: (%d, %d)", clicked.row,
          clicked.col);
  logMessage("[GAME]", log);

  bool moveMade = false;
  if (game->selectedPiece.row != -1) {
    sprintf(log, "Seçili taş var: (%d, %d). Hamle deneniyor...",
            game->selectedPiece.row, game->selectedPiece.col);
    logMessage("[GAME]", log);
    for (int i = 0; i < game->moveCount; i++) {
      if (game->possibleMoves[i].from.row == game->selectedPiece.row &&
          game->possibleMoves[i].from.col == game->selectedPiece.col &&
          game->possibleMoves[i].to.row == clicked.row &&
          game->possibleMoves[i].to.col == clicked.col) {

        Game_MakeMove(game, game->selectedPiece, clicked);
        moveMade = true;

        if (game->moveCount == 0) {
          logMessage("[GAME]", "Oyun bitti! Rakibin geçerli hamlesi kalmadı.");
          game->currentState = STATE_GAME_OVER;
          game->winner = (game->currentPlayer == 1) ? 2 : 1;
          char winLog[50];
          sprintf(winLog, "Kazanan oyuncu: %d", game->winner);
          logMessage("[GAME]", winLog);
        }
        break;
      }
    }
  }

  if (!moveMade) {
    logMessage("[GAME]", "Yeni bir taş seçimi yapılıyor veya mevcut seçim iptal ediliyor.");
    game->selectedPiece = (Koordinat){-1, -1};
    for (int i = 0; i < game->moveCount; i++) {
      if (game->possibleMoves[i].from.row == clicked.row &&
          game->possibleMoves[i].from.col == clicked.col) {
        game->selectedPiece = clicked;
        sprintf(log, "Yeni taş seçildi: (%d, %d)", game->selectedPiece.row,
                game->selectedPiece.col);
        logMessage("[GAME]", log);
        break;
      }
    }
  }
}

void Game_HandleMenuClick(Game *game, int x, int y) {
  if (game->currentState != STATE_MAIN_MENU)
    return;

  // Dil Değiştirme Butonu: {LOGICAL_WIDTH - 260, 40, 220, 70}
  if (x >= LOGICAL_WIDTH - 260 && x <= LOGICAL_WIDTH - 40 && y >= 40 && y <= 110) {
    game->language = (game->language == 0) ? 1 : 0;
    logMessage("[MENU]", game->language == 0 ? "Dil secildi: Turkce" : "Language selected: English");
    return;
  }

  // PVP Butonu: {LOGICAL_WIDTH / 2 - 300, 380, 600, 110}
  if (x >= LOGICAL_WIDTH / 2 - 300 && x <= LOGICAL_WIDTH / 2 + 300 && y >= 380 &&
      y <= 490) {
    game->isPvE = false;
    logMessage("[MENU]", "Mod seçildi: İki Kişilik (PVP)");
  }

  // PVE Butonu: {LOGICAL_WIDTH / 2 - 300, 510, 600, 110}
  if (x >= LOGICAL_WIDTH / 2 - 300 && x <= LOGICAL_WIDTH / 2 + 300 && y >= 510 &&
      y <= 620) {
    game->isPvE = true;
    logMessage("[MENU]", "Mod seçildi: Bilgisayara Karşı (PVE)");
  }

  if (game->isPvE) {
    // Taraf Seçimi (White: -210..-10, Black: +10..+210 @ 740..820)
    int cx = LOGICAL_WIDTH / 2;

    if (x >= cx - 210 && x <= cx - 10 && y >= 740 && y <= 820) {
      game->aiPlayer = 2; // User Beyaz(1), AI Siyah(2)
      logMessage("[MENU]", "Taraf seçildi: Beyaz (AI Siyah)");
    }
    if (x >= cx + 10 && x <= cx + 210 && y >= 740 && y <= 820) {
      game->aiPlayer = 1; // User Siyah(2), AI Beyaz(1)
      logMessage("[MENU]", "Taraf seçildi: Siyah (AI Beyaz)");
    }

    // Zorluk Seçimi (Çok Kolay, Kolay, Orta, Zor, Çok Zor)
    // 5 buton, genişlik 136, boşluk 16. Toplam Genişlik = 744.
    // Başlangıç X = (LOGICAL_WIDTH - 744) / 2 = 428
    // Y = 920, Yükseklik = 80
    int depths[] = {4, 6, 8, 10, 12};
    int btnWidth = 136;
    int btnHeight = 80;
    int gap = 16;
    int totalWidth = (5 * btnWidth) + (4 * gap);

    int startX = (LOGICAL_WIDTH - totalWidth) / 2;
    int btnY = 920;

    if (y >= btnY && y <= btnY + btnHeight) {
      for (int i = 0; i < 5; i++) {
        int btnX = startX + i * (btnWidth + gap);
        if (x >= btnX && x <= btnX + btnWidth) {
          game->minimaxDepth = depths[i];
          char log[50];
          sprintf(log, "Zorluk (Derinlik): %d", depths[i]);
          logMessage("[MENU]", log);
          break;
        }
      }
    }
  }

  // Başlat Butonu: {LOGICAL_WIDTH / 2 - 250, start_y, 500, 110}
  // If game->isPvE: y is [1150, 1260]. Otherwise: y is [680, 790]
  float start_y = game->isPvE ? 1150.0f : 680.0f;
  if (x >= LOGICAL_WIDTH / 2 - 250 && x <= LOGICAL_WIDTH / 2 + 250 && y >= start_y && y <= start_y + 110) {
    Game_Start(game);
    logMessage("[MENU]", "Oyun başlatıldı.");
  }
}
