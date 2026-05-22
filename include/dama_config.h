// DamaC/include/dama_config.h
#ifndef DAMA_CONFIG_H
#define DAMA_CONFIG_H

// --- Pencere ve Ekran Fiziksel Ayarları ---
#define SCREEN_WIDTH 800
#define SCREEN_HEIGHT 900 
#define WINDOW_TITLE "Türk Daması [v2]"

// --- Mantıksal Çözünürlük (HiDPI için 2x Ölçekli Çözünürlük) ---
#define LOGICAL_WIDTH 1600
#define LOGICAL_HEIGHT 1800

// --- Oyun Tahtası Ayarları (Mantıksal Koordinatlar Üzerinden) ---
#define BOARD_SIZE 8
#define BOARD_OFFSET 80 // Fiziksel olarak 40 pikseldi, mantıksal olarak 2x ölçekte 80 oldu.
#define BOARD_AREA_SIZE (LOGICAL_WIDTH - (BOARD_OFFSET * 2)) // 1440 piksel
#define SQUARE_SIZE (BOARD_AREA_SIZE / BOARD_SIZE) // 180 piksel

#endif // DAMA_CONFIG_H
