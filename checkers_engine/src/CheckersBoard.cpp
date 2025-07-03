#include "CheckersBoard.h"
#include <iostream>
#include <sstream>
#include <algorithm>

// --- Move struct implementation ---
std::string Move::to_string() const {
    std::stringstream ss;
    ss << "Path: ";
    for (size_t i = 0; i < path.size(); ++i) {
        ss << path[i] << (i == path.size() - 1 ? "" : " -> ");
    }
    ss << ", Captures: " << pieces_captured;
    return ss.str();
}

// --- CheckersBoard class implementation ---

CheckersBoard::CheckersBoard() {
    setup_new_game();
}

void CheckersBoard::setup_new_game() {
    // Türk Daması başlangıç dizilimi
    white_pieces = 0x0000FFFF00000000ULL; // Sıra 2 ve 3
    black_pieces = 0x00000000FFFF0000ULL; // Sıra 5 ve 6
    kings = 0;
    white_to_move = true;
}

std::vector<Move> CheckersBoard::get_legal_moves() {
    // Bu fonksiyonun tam implementasyonu sonraki adımlarda yapılacak.
    // Şimdilik boş bir vektör döndürüyor.
    std::vector<Move> moves;
    // 1. Taş alma hamlelerini ara
    // 2. Yoksa, normal hamleleri ara
    // 3. En uzun alım kuralını uygula
    return moves;
}

void CheckersBoard::do_move(const Move& move) {
    // Bu fonksiyonun tam implementasyonu sonraki adımlarda yapılacak.
}

int CheckersBoard::get_game_outcome() {
    // Bu fonksiyonun tam implementasyonu sonraki adımlarda yapılacak.
    return 0; // Oyun devam ediyor
}

std::string CheckersBoard::to_fen() const {
    // Tahta durumunu FEN string'ine çevir (saklama/yükleme için)
    // Bu fonksiyonun tam implementasyonu sonraki adımlarda yapılacak.
    return "";
}

void CheckersBoard::load_fen(const std::string& fen_string) {
    // FEN string'inden tahta durumunu yükle
    // Bu fonksiyonun tam implementasyonu sonraki adımlarda yapılacak.
}

void CheckersBoard::print_board() const {
    std::cout << "\n  a b c d e f g h" << std::endl;
    std::cout << " +-----------------+" << std::endl;
    for (int r = 0; r < 8; ++r) {
        std::cout << 8 - r << "|";
        for (int c = 0; c < 8; ++c) {
            int sq_flipped = (7 - r) * 8 + c;
            char piece = '.';
            if ((white_pieces & (1ULL << sq_flipped)))
                piece = (kings & (1ULL << sq_flipped)) ? 'W' : 'w';
            else if ((black_pieces & (1ULL << sq_flipped)))
                piece = (kings & (1ULL << sq_flipped)) ? 'B' : 'b';
            std::cout << " " << piece;
        }
        std::cout << " |" << 8 - r << std::endl;
    }
    std::cout << " +-----------------+" << std::endl;
    std::cout << "  a b c d e f g h" << std::endl;
    std::cout << (white_to_move ? "Sıra Beyaz'da" : "Sıra Siyah'da") << std::endl;
}
