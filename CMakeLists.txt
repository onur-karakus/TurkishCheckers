cmake_minimum_required(VERSION 3.16)
project(Dama LANGUAGES C)

# C Standardı Ayarı (C99 veya C11)
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

# Derleyici Uyarıları (Yüksek kod kalitesi için)
if(MSVC)
    add_compile_options(/W4)
else()
    add_compile_options(-Wall -Wextra -O3)
endif()

# SDL3 Kütüphanesini Bul
find_package(SDL3 REQUIRED)

# Başlık (Header) Dizinleri
include_directories(include)

# Kaynak Dosyalar
set(SOURCES
    src/dama_main.c
    src/dama_game.c
    src/dama_renderer.c
    src/dama_ai.c
)

# Çalıştırılabilir İkili (Executable) Oluştur
add_executable(Dama ${SOURCES})

# SDL3 Kütüphanesini Bağla (Linker)
target_link_libraries(Dama PRIVATE SDL3::SDL3)

# Platforma özel ayarlar (Windows için konsol penceresini gizleme vb. istenirse)
if(WIN32)
    # Windows'ta konsol penceresi yerine doğrudan GUI penceresi açılması için:
    set_target_properties(Dama PROPERTIES WIN32_EXECUTABLE ON)
endif()
