#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include "CheckersBoard.h"

namespace py = pybind11;

// PYBIND11_MODULE makrosu, 'checkers_engine' adında bir Python modülü oluşturur.
PYBIND11_MODULE(checkers_engine, m) {
    m.doc() = "High-performance C++ checkers engine with Python bindings";

    // Move yapısını Python'a tanıt
    py::class_<Move>(m, "Move")
        .def(py::init<>())
        .def_readwrite("path", &Move::path)
        .def_readwrite("is_capture", &Move::is_capture)
        .def_readwrite("pieces_captured", &Move::pieces_captured)
        .def("__repr__", &Move::to_string); // Python'da print() ile güzel görünmesi için

    // CheckersBoard sınıfını ve fonksiyonlarını Python'a bağla
    py::class_<CheckersBoard>(m, "Board")
        .def(py::init<>()) // Kurucu fonksiyonu bağla
        .def("setup_new_game", &CheckersBoard::setup_new_game)
        .def("get_legal_moves", &CheckersBoard::get_legal_moves)
        .def("do_move", &CheckersBoard::do_move)
        .def("get_game_outcome", &CheckersBoard::get_game_outcome)
        .def("to_fen", &CheckersBoard::to_fen, "Returns the board state as a FEN string.")
        .def("load_fen", &CheckersBoard::load_fen, "Loads a board state from a FEN string.")
        .def("print_board", &CheckersBoard::print_board)
        // Bitboard'ları Python'dan okuyabilmek için özellikler ekle
        .def_property_readonly("white_pieces", [](const CheckersBoard &b) { return b.white_pieces; })
        .def_property_readonly("black_pieces", [](const CheckersBoard &b) { return b.black_pieces; })
        .def_property_readonly("kings", [](const CheckersBoard &b) { return b.kings; })
        .def_property("white_to_move",
            [](const CheckersBoard &b) { return b.white_to_move; },
            [](CheckersBoard &b, bool wtm) { b.white_to_move = wtm; }
        );
}
