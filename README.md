# 🏁 Türk Daması &mdash; Turkish Checkers (SDL3 & C)

[![Language](https://img.shields.io/badge/Language-C-blue.svg)](#)
[![Library](https://img.shields.io/badge/Graphics-SDL3-red.svg)](#)
[![OS](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)

A high-performance, retro-modern implementation of the traditional **Turkish Checkers (Dama)** game built using **SDL3** and pure **C**. Designed to run seamlessly across **Windows**, **Linux**, and **macOS**, it features a robust minimax-based AI engine, multi-threaded pondering, full game replay support, and an elegant, responsive user interface.

---

## 🌍 Dil Seçimi / Language Selection
- [Türkçe Kılavuz](#tr-türk-daması)
- [English Guide](#en-turkish-checkers)

---

# [TR] Türk Daması

Bu proje, geleneksel Türk Daması kurallarını temel alan, **C** dilinde **SDL3** kütüphanesi kullanılarak geliştirilmiş modern, yüksek performanslı ve tamamen platformlar arası (Windows, Linux, macOS) bir masa oyunudur.

## ✨ Temel Özellikler

* **🤖 Gelişmiş Yapay Zeka (AI):**
  * **Minimax Arama:** Ayarlanabilir zorluk dereceleri (Arama Derinliği).
  * **Alfa-Beta Budama (Alpha-Beta Pruning):** Gereksiz oyun ağaçlarını budayarak yüksek hızda en iyi hamle analizi.
  * **Arka Plan Düşünme (Pondering):** Sıra oyuncudayken yapay zekanın arka planda (multi-thread) hamle tahminleri yapması ve zaman kazanması.
* **📜 Hamle Geçmişi & Tekrar Oynatma (Replay):**
  * Yapılan tüm hamleleri notasyon sistemiyle kaydetme.
  * Oyun sırasında veya oyun bittiğinde geriye ve ileriye dönük hamle geçmişini adım adım izleme imkanı (Undo/Redo & Replay).
* **🎨 Modern Görsel Mimari (Retina/HiDPI):**
  * SDL3'ün mantıksal çözünürlük ölçeklemesi sayesinde tüm ekranlarda (ve Retina ekranlarda) kristal netliğinde grafikler.
  * Akıcı mikro-animasyonlar, taş seçim belirteçleri ve son yapılan hamlenin vurgulanması.
  * Gözü yormayan modern, karanlık mod uyumlu renk paleti.
* **🌐 Çift Dil Desteği:**
  * Türkçe ve İngilizce dilleri arasında dinamik geçiş olanağı.
* **🖥️ Platformlar Arası (Cross-Platform) Mimari:**
  * Herhangi bir platform bağımlılığı içermeyen saf C ve SDL3 yapısı ile Windows, Linux ve macOS üzerinde sıfır değişiklik ile derlenebilme.

## 🛠️ Kurulum ve Gereksinimler

Projenin derlenebilmesi için sisteminizde **SDL3** kütüphanesinin yüklü olması gerekir.

### 🍎 macOS Kurulumu
1. [Homebrew](https://brew.sh/) yardımıyla SDL3 kütüphanesini yükleyin:
   ```bash
   brew install sdl3
   ```

### 🐧 Linux (Ubuntu/Debian) Kurulumu
1. Paket yöneticinizle SDL3 geliştirme kütüphanelerini yükleyin:
   ```bash
   sudo apt update
   sudo apt install cmake gcc libsdl3-dev
   ```

### 💻 Windows Kurulumu
1. [SDL3 Resmi Sürüm Sayfasından](https://github.com/libsdl-org/SDL/releases) Windows geliştirme kütüphanesini indirin veya paket yöneticisi (vcpkg vb.) kullanarak kurun.

---

## 🚀 Derleme ve Çalıştırma

### 1. CMake ile Derleme (Tüm İşletim Sistemleri - Önerilen)
Sisteminizde CMake yüklü ise, terminalden aşağıdaki komutlarla projeyi derleyebilirsiniz:

```bash
# Yapılandırma klasörünü oluştur
cmake -B build

# Projeyi derle
cmake --build build

# Oyunu Çalıştır:
# macOS/Linux:
./build/Dama
# Windows:
.\build\Debug\Dama.exe
```

### 2. macOS Yerel `Makefile` ile Derleme
Sadece macOS işletim sistemine özel hızlı derleme ve çalıştırılabilir uygulama paketi (`Dama.app`) üretimi için `Makefile` dosyasını kullanabilirsiniz:

```bash
# Derleme ve Dama.app paketi oluşturma
make

# Oyunu çalıştırma
make run

# Derleme artıklarını temizleme
make clean
```

## ⚙️ Yapılandırma ve Hata Ayıklama (VS Code)

Proje, VS Code ile tam entegre çalışacak şekilde yapılandırılmıştır:
* **`detect_sdl3.sh`:** Sisteminizdeki SDL3 yollarını otomatik olarak tarar ve doğrular.
* **`tasks.json`:** `make` ve `make clean` işlemlerini doğrudan VS Code içinden çalıştırmanızı sağlar.
* **`launch.json`:** macOS üzerinde **LLDB** hata ayıklayıcısıyla projeyi tek tıkla analiz etmenize ve debug yapmanıza olanak tanır.

---

# [EN] Turkish Checkers

A high-performance, modern implementation of the traditional **Turkish Checkers (Dama)** game built using **SDL3** and pure **C**. Designed to run seamlessly across **Windows**, **Linux**, and **macOS**.

## ✨ Key Features

* **🤖 Advanced AI Engine:**
  * **Minimax Search:** Multi-level depth options to adjust difficulty.
  * **Alpha-Beta Pruning:** Fast, pruned search trees for quick and intelligent decision-making.
  * **Background Pondering:** Multi-threaded analysis running in the background during the player's turn to predict future moves.
* **📜 Move History & Replay System:**
  * Comprehensive notation logs for all played moves.
  * Step-by-step game navigation (Undo, Redo, and Replay) during or after the match.
* **🎨 Modern Visuals & HiDPI/Retina Support:**
  * Native logical presentation scaling in SDL3 for crisp rendering on high-density displays (such as Apple Retina).
  * Micro-animations, active highlights, and indicators for selected pieces and last moves.
  * Sleek, harmonious dark-theme aesthetics.
* **🌐 Dynamic Localization:**
  * Instant switching between Turkish and English.
* **🖥️ Fully Cross-Platform:**
  * Developed entirely in standard C99 without platform-specific dependencies, ensuring native builds on Windows, Linux, and macOS.

## 🛠️ Prerequisites & Installation

To build and run this application, you must install **SDL3**.

### 🍎 macOS
1. Install SDL3 using [Homebrew](https://brew.sh/):
   ```bash
   brew install sdl3
   ```

### 🐧 Linux (Ubuntu/Debian)
1. Install development headers and compiler tools via your package manager:
   ```bash
   sudo apt update
   sudo apt install cmake gcc libsdl3-dev
   ```

### 💻 Windows
1. Download Windows development binaries from [SDL3 Releases Page](https://github.com/libsdl-org/SDL/releases) or manage it via package managers like `vcpkg`.

---

## 🚀 Building and Running

### 1. Building via CMake (All Platforms - Recommended)
If CMake is installed on your system, you can generate build files and compile the executable using the following commands:

```bash
# Generate build configuration
cmake -B build

# Build the project
cmake --build build

# Run the game:
# macOS/Linux:
./build/Dama
# Windows:
.\build\Debug\Dama.exe
```

### 2. Building via Native Makefile (macOS Only)
For a macOS-specific quick compile and package generator (`Dama.app`), you can use the standard Makefile:

```bash
# Compile and create application bundle
make

# Run the application
make run

# Clean intermediate build outputs
make clean
```

## ⚙️ Development Environment (VS Code)

This repository includes a complete workspace structure for VS Code:
* **`detect_sdl3.sh`:** Autodetects Homebrew and SDL3 framework headers/libraries on your system.
* **`tasks.json`:** Standardized task definitions for compiling the codebase via `make`.
* **`launch.json`:** Out-of-the-box debug configuration to inspect variables and debug execution via **LLDB**.

---

## 📜 Oynanış ve Kurallar / Gameplay & Rules

### 🇹🇷 Oynanış
Türk daması 64 kareden oluşan 8x8 bir tahta üzerinde 16'sı siyah, 16'sı beyaz olarak 32 taş ile oynanır. İkinci ve üçüncü sıraya beyaz taşlar, altıncı ve yedinci sıraya siyah taşlar dizilir ve oyuna beyaz taraf başlar. Taşlar, klasik damanın aksine çapraz hareket etmez, komşu kareler boş ise sağa, sola ve ileri hareket edebilir fakat geri gidemez. Bütün taşların amacı en ileri sıradaki kareye ulaşıp "dama" olmaktır. Dama olarak güçlenen taş geri hareket kabiliyeti kazanır, ayrıca karşı tarafın bir veya birkaç taşını almak şartıyla birden fazla karede L şeklinde hareket edebilir. Taşlar arasında en kıymetli taş dama olarak adlandırılan bu taştır. Damaya ulaşamamış taşlar "yoz" olarak adlandırılır. Dama olmuş taşın hareket kabiliyeti yüksek olduğu için (oyuncunun ustalık derecesine göre) dama, 5 yoz taş değerinde görülür, yani bir dama taşı elde edebilmek için 5 yoz taş feda edilebilir.

Türk damasında amaç karşı tarafın taşlarını tüketip oyunu kazanmaktır. Her iki oyuncunun da bir hamle hakkı vardır. Bir taraf hamlesini yaptıktan sonra sıra karşı tarafa geçer. Oyun sonunda her iki tarafın da bir taşı kalmışsa (taşlardan biri dama olsa bile), oyun beraberlikle sonuçlanır ve bu durum **"gayyım"** olarak adlandırılır.

### 🇹🇷 Kurallar
* Her iki oyuncu da kendisinin bastığı (Taşını istediği), gerekse rakibin bilerek verdiği taşların hepsini ilk hamlede almak mecburiyetindedir.
* Eğer bir oyuncu iki taraflı taş almak kabil olan bir hamleye basar, (Taş isterse) ve bu taşların adetleri eşit olursa oyuncu dilediği tarafa taş almakta serbesttir.
* Ayrı ayrı taşları birkaç yerden taş almak mecburiyetinde bulunsa bile evvele çok alınan taraftaki taşları toplamak zorundadır.
* Damaya çıkmış bir taş için dahi bu mecburiyet kesindir.
* Yoz taş, taş alarak damaya çıkıyorsa ve bitişikte taş varsa yoz taş gibi taş almaya devam eder.
* Dama olan taş dama sahası dışında ortada bulunamaz.

---

### 🇬🇧 Gameplay
Turkish checkers is played on an 8x8 board with 64 squares, using 32 pieces (16 white, 16 black). White pieces are placed on the 2nd and 3rd rows, black pieces on the 6th and 7th rows. White moves first. Unlike classical checkers, pieces do not move diagonally. If the adjacent squares are empty, they can move right, left, and forward, but never backward. The goal of all pieces is to reach the furthest row to promote to **"Dama"** (King). A promoted Dama gains backward movement and can move across multiple empty squares orthogonally, turning in an L-shape if capturing opponent pieces. The Dama is the most valuable piece. Non-promoted pieces are called **"yoz"** (pawns). Due to its high mobility, a Dama is valued at 5 yoz pieces (i.e., one can sacrifice 5 pawns to obtain a Dama).

The objective is to capture all opponent pieces to win the game. Each player has one turn. If only one piece remains for each side at the end of the game (even if one is a Dama), the game ends in a draw, known as **"gayyım"**.

### 🇬🇧 Rules
* Standard captures are mandatory: players must capture whenever they have the opportunity.
* If a player has multiple capturing options with an equal number of pieces to be captured, they are free to choose any route.
* If there are multiple capturing opportunities with different numbers of pieces, the route capturing the maximum number of pieces must be taken first. This applies to Damas as well.
* If a pawn (yoz) reaches the back row via a capture and there are further adjacent captures available, it must continue capturing as a pawn (yoz). It only becomes a fully functioning Dama at the end of its turn.
* A promoted Dama cannot be created in the middle of the board (outside the promotion row).

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
