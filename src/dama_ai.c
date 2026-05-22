// DamaC/src/dama_ai.c

#include "dama_ai.h"
#include <SDL3/SDL.h> // Added for threading
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// --- Sabitler ve Veri Yapıları ---

#define TT_SIZE 1000000 // 1 Milyon giriş

typedef unsigned long long U64;

typedef enum { HASH_EXACT, HASH_ALPHA, HASH_BETA } HashFlag;

typedef struct {
  U64 key;
  int depth;
  int score;
  int flag; // 0: EXACT, 1: LOWERBOUND, 2: UPPERBOUND (Changed from HashFlag)
  Hamle bestMove;
} TTEntry;

static TTEntry *tt = NULL; // Changed to pointer
static unsigned long long
    zKey[8][8][5]; // [row][col][piece_type] (Replaced zobristKeys)
static unsigned long long zBlackMove; // Siyah hamle sırası için (Added)

// --- Global Değişkenler ---
// Durdurma Bayrağı (Thread güvenliği için volatile)
static volatile int g_aiStopRequest = 0;
static SDL_Thread *g_ponderThread = NULL;
static Game g_ponderGameCopy; // Thread'in üzerinde çalışacağı kopya oyun

// --- Helper Fonksiyon Prototipleri ---
static U64 rand_u64();
static U64 computeZobristKey(TasTipi p_board[BOARD_SIZE][BOARD_SIZE],
                             int currentPlayer); // Updated prototype
static int probeTT(U64 key, int depth, int alpha, int beta, Hamle *bestMove);
static void storeTT(U64 key, int depth, int score, HashFlag flag,
                    Hamle bestMove);
static int evaluateBoard(TasTipi p_board[BOARD_SIZE][BOARD_SIZE], int aiColor);
static int quiescenceSearch(TasTipi p_board[BOARD_SIZE][BOARD_SIZE], int alpha,
                            int beta, int p_currentPlayer, int aiColor,
                            Koordinat lockedPiece);
static int minimax(TasTipi p_board[BOARD_SIZE][BOARD_SIZE], int depth,
                   int alpha, int beta, bool isMaximizing, int p_currentPlayer,
                   int aiColor, U64 currentKey, Koordinat lockedPiece);

// --- Implementasyon ---

static U64 rand_u64() { return ((U64)rand() << 32) | rand(); }

void AI_Init() {
  srand((unsigned int)time(NULL));
  tt = (TTEntry *)calloc(TT_SIZE, sizeof(TTEntry));
  if (!tt) {
    printf("[AI] FATAL: Hash tablosu için bellek ayrılamadı!\n");
  }
  for (int i = 0; i < 8; i++) {
    for (int j = 0; j < 8; j++) {
      for (int k = 0; k < 5; k++) {
        zKey[i][j][k] = rand_u64();
      }
    }
  }
  zBlackMove = rand_u64();
}

static void clearTT() {
  if (tt)
    memset(tt, 0, (size_t)TT_SIZE * sizeof(TTEntry));
}

static U64 computeZobristKey(TasTipi p_board[BOARD_SIZE][BOARD_SIZE],
                             int currentPlayer) {
  U64 key = 0;
  for (int i = 0; i < 8; i++) {
    for (int j = 0; j < 8; j++) {
      if (p_board[i][j] != BOS_KARE) {
        int typeIndex = 0;
        if (p_board[i][j] == BEYAZ_TAS)
          typeIndex = 1;
        else if (p_board[i][j] == SIYAH_TAS)
          typeIndex = 2;
        else if (p_board[i][j] == BEYAZ_DAMA)
          typeIndex = 3;
        else if (p_board[i][j] == SIYAH_DAMA)
          typeIndex = 4;

        key ^= zKey[i][j][typeIndex];
      }
    }
  }
  if (currentPlayer == 2) {
    key ^= zBlackMove;
  }
  return key;
}

static int probeTT(U64 key, int depth, int alpha, int beta, Hamle *bestMove) {
  if (!tt)
    return INT_MIN;
  TTEntry *entry = &tt[key % TT_SIZE];
  if (entry->key == key) {
    *bestMove = entry->bestMove;
    if (entry->depth >= depth) {
      if (entry->flag == HASH_EXACT)
        return entry->score;
      if (entry->flag == HASH_ALPHA && entry->score <= alpha)
        return entry->score;
      if (entry->flag == HASH_BETA && entry->score >= beta)
        return entry->score;
    }
  }
  return INT_MIN;
}

static void storeTT(U64 key, int depth, int score, HashFlag flag,
                    Hamle bestMove) {
  if (!tt)
    return;
  TTEntry *entry = &tt[key % TT_SIZE];
  if (entry->key != key || depth >= entry->depth) {
    entry->key = key;
    entry->depth = depth;
    entry->score = score;
    entry->flag = flag;
    if (bestMove.from.row != -1) {
      entry->bestMove = bestMove;
    }
  }
}

static int evaluateBoard(TasTipi p_board[BOARD_SIZE][BOARD_SIZE], int aiColor) {
  int white_score = 0;
  int black_score = 0;

  int piece_square_table[8][8] = {
      {0, 0, 0, 0, 0, 0, 0, 0}, {1, 2, 3, 3, 3, 3, 2, 1},
      {2, 3, 4, 5, 5, 4, 3, 2}, {3, 4, 5, 6, 6, 5, 4, 3},
      {3, 4, 5, 6, 6, 5, 4, 3}, {2, 3, 4, 5, 5, 4, 3, 2},
      {1, 2, 3, 3, 3, 3, 2, 1}, {0, 0, 0, 0, 0, 0, 0, 0}};

  for (int r = 0; r < 8; r++) {
    for (int c = 0; c < 8; c++) {
      TasTipi piece = p_board[r][c];
      if (piece == BEYAZ_TAS) {
        white_score += 100 + piece_square_table[r][c];
      } else if (piece == BEYAZ_DAMA) {
        white_score += 500;
      } else if (piece == SIYAH_TAS) {
        black_score += 100 + piece_square_table[7 - r][c];
      } else if (piece == SIYAH_DAMA) {
        black_score += 500;
      }
    }
  }

  if (aiColor == 2) {
    return black_score - white_score;
  } else {
    return white_score - black_score;
  }
}

static int quiescenceSearch(TasTipi p_board[BOARD_SIZE][BOARD_SIZE], int alpha,
                            int beta, int p_currentPlayer, int aiColor,
                            Koordinat lockedPiece) {
  int stand_pat = evaluateBoard(p_board, aiColor);

  if (p_currentPlayer == aiColor) { // Maximizing
    if (stand_pat >= beta)
      return beta;
    if (stand_pat > alpha)
      alpha = stand_pat;
  } else { // Minimizing
    if (stand_pat <= alpha)
      return alpha;
    if (stand_pat < beta)
      beta = stand_pat;
  }

  Hamle moves[256];
  int count = 0;
  bool isCaptureMandatory = false;

  if (lockedPiece.row != -1) {
    Game_FindMovesForLockedPiece(p_board, p_currentPlayer, lockedPiece, moves,
                                 &count);
    if (count > 0) {
      if (abs(moves[0].from.row - moves[0].to.row) > 1 ||
          abs(moves[0].from.col - moves[0].to.col) > 1) {
        isCaptureMandatory = true;
      }
    }
  } else {
    Game_FindAllPossibleMovesForBoard(p_board, p_currentPlayer, moves, &count,
                                      &isCaptureMandatory);
  }

  if (!isCaptureMandatory || count == 0) {
    return stand_pat;
  }

  for (int i = 0; i < count; i++) {
    TasTipi nextBoard[BOARD_SIZE][BOARD_SIZE];
    memcpy(nextBoard, p_board, sizeof(TasTipi) * BOARD_SIZE * BOARD_SIZE);

    bool chainContinues = Game_SimulateMove(nextBoard, moves[i].from,
                                             moves[i].to, isCaptureMandatory);

    Koordinat nextLocked = chainContinues ? moves[i].to : (Koordinat){-1, -1};

    int score = quiescenceSearch(nextBoard, alpha, beta, p_currentPlayer,
                                 aiColor, nextLocked);

    if (p_currentPlayer == aiColor) { // Maximizing
      if (score >= beta)
        return beta;
      if (score > alpha)
        alpha = score;
    } else { // Minimizing
      if (score <= alpha)
        return alpha;
      if (score < beta)
        beta = score;
    }
  }

  return (p_currentPlayer == aiColor) ? alpha : beta;
}

typedef struct {
  Hamle move;
  int score;
} ScoredMove;

static int scoreMove(TasTipi p_board[BOARD_SIZE][BOARD_SIZE], Hamle move, Hamle ttMove) {
  if (ttMove.from.row == move.from.row && ttMove.from.col == move.from.col &&
      ttMove.to.row == move.to.row && ttMove.to.col == move.to.col) {
    return 100000;
  }

  int score = 0;
  TasTipi piece = p_board[move.from.row][move.from.col];

  if (piece == BEYAZ_TAS && move.to.row == 0) score += 500;
  if (piece == SIYAH_TAS && move.to.row == 7) score += 500;

  int r_diff = move.to.row - move.from.row;
  int c_diff = move.to.col - move.from.col;
  if (abs(r_diff) > 1 || abs(c_diff) > 1) {
    if (piece == BEYAZ_DAMA || piece == SIYAH_DAMA) {
      int r_step = (r_diff > 0) ? 1 : ((r_diff < 0) ? -1 : 0);
      int c_step = (c_diff > 0) ? 1 : ((c_diff < 0) ? -1 : 0);
      for (int i = 1;; i++) {
        Koordinat current = {move.from.row + i * r_step, move.from.col + i * c_step};
        if (current.row == move.to.row && current.col == move.to.col)
          break;
        TasTipi capturedPiece = p_board[current.row][current.col];
        if (capturedPiece == BEYAZ_DAMA || capturedPiece == SIYAH_DAMA) {
          score += 200;
          break;
        }
      }
    } else {
      TasTipi capturedPiece = p_board[(move.from.row + move.to.row) / 2][(move.from.col + move.to.col) / 2];
      if (capturedPiece == BEYAZ_DAMA || capturedPiece == SIYAH_DAMA) {
        score += 200;
      }
    }
  }

  return score;
}

static int minimax(TasTipi p_board[BOARD_SIZE][BOARD_SIZE], int depth,
                   int alpha, int beta, bool isMaximizing, int p_currentPlayer,
                   int aiColor, U64 currentKey, Koordinat lockedPiece) {
  if (g_aiStopRequest)
    return 0;

  Hamle ttMove = {{-1, -1}, {-1, -1}};
  int tt_score = probeTT(currentKey, depth, alpha, beta, &ttMove);
  if (tt_score != INT_MIN) {
    return tt_score;
  }

  if (depth == 0) {
    return quiescenceSearch(p_board, alpha, beta, p_currentPlayer, aiColor,
                            lockedPiece);
  }

  Hamle moves[256];
  int count = 0;
  bool isCaptureMandatory = false;

  if (lockedPiece.row != -1) {
    Game_FindMovesForLockedPiece(p_board, p_currentPlayer, lockedPiece, moves,
                                 &count);
    if (count > 0) {
      if (abs(moves[0].from.row - moves[0].to.row) > 1 ||
          abs(moves[0].from.col - moves[0].to.col) > 1) {
        isCaptureMandatory = true;
      }
    }
  } else {
    Game_FindAllPossibleMovesForBoard(p_board, p_currentPlayer, moves, &count,
                                      &isCaptureMandatory);
  }

  if (count == 0) {
    if (isMaximizing)
      return -100000 + (10 - depth); // AI kaybetti
    else
      return 100000 - (10 - depth); // AI kazandı
  }

  // Move Ordering (Hamle Sıralama)
  if (count > 1) {
    ScoredMove scoredMoves[256];
    for (int i = 0; i < count; i++) {
      scoredMoves[i].move = moves[i];
      scoredMoves[i].score = scoreMove(p_board, moves[i], ttMove);
    }
    // Sort moves in descending order of score
    for (int i = 0; i < count - 1; i++) {
      for (int j = i + 1; j < count; j++) {
        if (scoredMoves[j].score > scoredMoves[i].score) {
          ScoredMove temp = scoredMoves[i];
          scoredMoves[i] = scoredMoves[j];
          scoredMoves[j] = temp;
        }
      }
    }
    for (int i = 0; i < count; i++) {
      moves[i] = scoredMoves[i].move;
    }
  }

  Hamle bestMoveSoFar = moves[0];
  HashFlag flag = HASH_ALPHA;
  int bestVal = isMaximizing ? INT_MIN : INT_MAX;

  for (int i = 0; i < count; i++) {
    TasTipi nextBoard[BOARD_SIZE][BOARD_SIZE];
    memcpy(nextBoard, p_board, sizeof(TasTipi) * 64);

    bool chainContinues = Game_SimulateMove(nextBoard, moves[i].from,
                                             moves[i].to, isCaptureMandatory);

    int nextPlayer =
        chainContinues ? p_currentPlayer : ((p_currentPlayer == 1) ? 2 : 1);
    bool nextIsMax = chainContinues ? isMaximizing : !isMaximizing;

    Koordinat nextLocked = chainContinues ? moves[i].to : (Koordinat){-1, -1};

    U64 nextKey = computeZobristKey(nextBoard, nextPlayer);

    int val = minimax(nextBoard, depth - 1, alpha, beta, nextIsMax, nextPlayer,
                      aiColor, nextKey, nextLocked);

    if (g_aiStopRequest)
      return 0;

    if (isMaximizing) {
      if (val > bestVal) {
        bestVal = val;
        bestMoveSoFar = moves[i];
      }
      if (bestVal > alpha)
        alpha = bestVal;
    } else {
      if (val < bestVal) {
        bestVal = val;
        bestMoveSoFar = moves[i];
      }
      if (bestVal < beta)
        beta = bestVal;
    }

    if (beta <= alpha)
      break;
  }

  if (bestVal <= alpha)
    flag = HASH_ALPHA;
  else if (bestVal >= beta)
    flag = HASH_BETA;
  else
    flag = HASH_EXACT;

  storeTT(currentKey, depth, bestVal, flag, bestMoveSoFar);
  return bestVal;
}

int PonderThreadFunc(void *data) {
  Game *gameCopy = (Game *)data;

  TasTipi boardCopy[8][8];
  for (int r = 0; r < 8; r++)
    for (int c = 0; c < 8; c++)
      boardCopy[r][c] = gameCopy->board[r][c];

  int ponderPlayer = gameCopy->currentPlayer;
  int ponderDepth = gameCopy->minimaxDepth;

  U64 ponderKey = computeZobristKey(boardCopy, ponderPlayer);

  minimax(boardCopy, ponderDepth, INT_MIN, INT_MAX, true, ponderPlayer,
          ponderPlayer, ponderKey, (Koordinat){-1, -1});

  return 0;
}

void AI_StartPondering(const Game *game) {
  if (g_ponderThread != NULL) {
    return;
  }

  g_ponderGameCopy = *game;
  g_aiStopRequest = 0;
  g_ponderThread =
      SDL_CreateThread(PonderThreadFunc, "AI_Ponder", &g_ponderGameCopy);
  if (!g_ponderThread) {
    printf("[AI] Ponder thread oluşturulamadı: %s\n", SDL_GetError());
  }
}

void AI_StopPondering() {
  if (g_ponderThread) {
    g_aiStopRequest = 1;
    int threadReturnValue;
    SDL_WaitThread(g_ponderThread, &threadReturnValue);
    g_ponderThread = NULL;
    g_aiStopRequest = 0;
  }
}

Hamle AI_GetBestMove(const Game *game) {
  if (!game)
    return (Hamle){{-1, -1}, {-1, -1}};

  int aiColor = game->currentPlayer;
  int targetDepth = game->minimaxDepth;

  Hamle bestMove = {{-1, -1}, {-1, -1}};
  int overallBestScore = INT_MIN;

  Hamle moves[256];
  int count = 0;
  bool isCaptureMandatory = false;
  Game_FindAllPossibleMovesForBoard((TasTipi(*)[8])game->board, aiColor, moves,
                                    &count, &isCaptureMandatory);

  if (count == 0)
    return bestMove;

  // Set default best move in case search is aborted instantly
  bestMove = moves[0];

  g_aiStopRequest = 0;

  // Iterative Deepening Loop
  for (int d = 1; d <= targetDepth; d++) {
    int bestScore = INT_MIN;
    Hamle currentIterationBestMove = moves[0];

    // Order root moves: put the best move from the previous iteration of iterative deepening first
    if (d > 1 && bestMove.from.row != -1) {
      for (int i = 0; i < count; i++) {
        if (moves[i].from.row == bestMove.from.row && moves[i].from.col == bestMove.from.col &&
            moves[i].to.row == bestMove.to.row && moves[i].to.col == bestMove.to.col) {
          Hamle temp = moves[0];
          moves[0] = moves[i];
          moves[i] = temp;
          break;
        }
      }
    }

    int alpha = INT_MIN;
    int beta = INT_MAX;

    for (int i = 0; i < count; i++) {
      TasTipi nextBoard[BOARD_SIZE][BOARD_SIZE];
      memcpy(nextBoard, game->board, sizeof(TasTipi) * 64);

      bool chainContinues = Game_SimulateMove(nextBoard, moves[i].from,
                                               moves[i].to, isCaptureMandatory);
      int nextPlayer = chainContinues ? aiColor : ((aiColor == 1) ? 2 : 1);
      bool nextIsMax = chainContinues ? true : false;

      Koordinat nextLocked = chainContinues ? moves[i].to : (Koordinat){-1, -1};

      U64 nextKey = computeZobristKey(nextBoard, nextPlayer);

      int val = minimax(nextBoard, d - 1, alpha, beta, nextIsMax, nextPlayer,
                        aiColor, nextKey, nextLocked);

      if (g_aiStopRequest) {
        break;
      }

      if (val > bestScore) {
        bestScore = val;
        currentIterationBestMove = moves[i];
      }
      if (bestScore > alpha)
        alpha = bestScore;
    }

    if (g_aiStopRequest) {
      printf("[AI] Iterasyon %d sirasinda arama durduruldu. Onceki en iyi hamle kullaniliyor.\n", d);
      break;
    }

    bestMove = currentIterationBestMove;
    overallBestScore = bestScore;
    printf("[AI] Derinlik %d tamamlandi. En iyi hamle: (%d,%d)->(%d,%d) Skor: %d\n",
           d, bestMove.from.row, bestMove.from.col, bestMove.to.row, bestMove.to.col,
           overallBestScore);
  }

  printf("[AI] Sonuc en iyi hamle: (%d,%d)->(%d,%d) Skor: %d\n",
         bestMove.from.row, bestMove.from.col, bestMove.to.row, bestMove.to.col,
         overallBestScore);

  return bestMove;
}
