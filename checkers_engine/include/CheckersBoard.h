#ifndef CHECKERS_BOARD_H
#define CHECKERS_BOARD_H

#include <cstdint>
#include <vector>
#include <string>

// 64-bit integer'ları bitboard olarak kullanacağız.
using Bitboard = uint64_t;

// Hamleleri temsil etmek için bir yapı.
// Türk damasında çoklu alımlar bir hamle sayıldığından,
// hamle yolunu (path) saklamak daha mantıklıdır.
struct Move {
    std::vector<int> path; // Hamlenin izlediği yol (örn: 12 -> 20 -> 36)
    bool is_capture = false;
    int pieces_captured = 0;

    // Python'da okunabilir bir temsil için
    std::string to_string() const;
};

class CheckersBoard {
public:
    // --- Bitboard'lar ---
    Bitboard white_pieces;
    Bitboard black_pieces;
    Bitboard kings;

    // --- Oyun Durumu ---
    bool white_to_move;

    // --- Kurucu Fonksiyon ---
    CheckersBoard();

    // --- Ana Fonksiyonlar ---
    void setup_new_game();
    std.vector<Move> get_legal_moves();
    void do_move(const Move& move);
    int get_game_outcome(); // 0: devam, 1: beyaz kazandı, -1: siyah kazandı, 2: berabere
    std::string to_fen() const;
    void load_fen(const std::string& fen_string);
    
    // --- Yardımcı Fonksiyonlar ---
    void print_board() const;

private:
    // --- Hamle Üretim Yardımcıları ---
    void generate_pawn_captures(std::vector<Move>& moves, bool is_white) const;
    void find_capture_paths(std::vector<Move>& all_paths, const std::vector<int>& current_path, Bitboard current_board, Bitboard opponent_board, bool is_dama) const;
    void generate_king_captures(std::vector<Move>& moves, bool is_white) const;
    void generate_normal_moves(std::vector<Move>& moves) const;
};

#endif // CHECKERS_BOARD_H
