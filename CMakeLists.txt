# CMake minimum sürümünü belirt
cmake_minimum_required(VERSION 3.12)

# Proje adını ve dilini tanımla
project(checkers_engine LANGUAGES CXX)

# C++ standardını ayarla (C++17)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# --- pybind11'i bul veya indir ---
# Bu blok, sistemde pybind11 kurulu değilse onu otomatik olarak indirir.
find_package(pybind11 CONFIG)
if (NOT pybind11_FOUND)
    include(FetchContent)
    FetchContent_Declare(
        pybind11
        GIT_REPOSITORY https://github.com/pybind/pybind11.git
        GIT_TAG v2.10.0 # Belirli bir versiyon kullanmak daha güvenilirdir
    )
    FetchContent_MakeAvailable(pybind11)
endif()

# --- Proje Kaynak Dosyalarını Tanımla ---
# Başlık dosyalarının bulunduğu klasörü belirt
include_directories(checkers_engine/include)

# Kaynak dosyaları bir değişkene ata
set(ENGINE_SOURCES
    checkers_engine/src/CheckersBoard.cpp
    py_bindings/bindings.cpp
)

# --- Python Modülünü Oluştur ---
# pybind11_add_module komutu, C++ kodundan bir Python eklentisi oluşturur.
# MODULE: Paylaşılan bir kütüphane (.so, .pyd) oluşturur.
pybind11_add_module(
    checkers_engine MODULE
    ${ENGINE_SOURCES}
)

# Hedef kütüphanenin özelliklerini ayarla
set_target_properties(checkers_engine PROPERTIES
    CXX_VISIBILITY_PRESET hidden
)
