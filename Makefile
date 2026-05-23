# Derleyici ve Program Adı
CC = clang
TARGET = Dama

# Homebrew Kurulum Yolu
BREW_PREFIX = /opt/homebrew

# C derleyici bayrakları
C_CFLAGS = -O3 -Iinclude -I$(BREW_PREFIX)/include

# Linker Flag'leri
LDFLAGS = -L$(BREW_PREFIX)/lib -lSDL3 -lSDL3_ttf -framework Cocoa -framework Foundation

# Kaynak Dosyalar
SRCS = src/dama_main.c src/dama_game.c src/dama_renderer.c src/dama_ai.c
OBJS = $(SRCS:.c=.o)

# .app Paketinin Yolları
APP_BUNDLE = $(TARGET).app
CONTENTS_DIR = $(APP_BUNDLE)/Contents
MACOS_DIR = $(CONTENTS_DIR)/MacOS
RESOURCES_DIR = $(CONTENTS_DIR)/Resources
PLIST_DEST = $(CONTENTS_DIR)/Info.plist
PLIST_SRC = Info.plist

# Ana Kural
all: $(APP_BUNDLE)

# .app paketini oluşturan kural
$(APP_BUNDLE): $(TARGET)
	@echo "Creating $(APP_BUNDLE)..."
	@mkdir -p $(MACOS_DIR)
	@mkdir -p $(RESOURCES_DIR)
	@cp $(TARGET) $(MACOS_DIR)/
	@echo "Copying Info.plist..."
	@cp $(PLIST_SRC) $(PLIST_DEST)
	@echo "Copying font.ttf to resources..."
	@cp font.ttf $(RESOURCES_DIR)/
	@echo "Fixing library paths for .app bundle..."
	@install_name_tool -add_rpath $(BREW_PREFIX)/lib $(MACOS_DIR)/$(TARGET)
	@echo "Signing the application bundle..."
	@codesign --force --deep --sign - $(APP_BUNDLE)
	@echo "Done."

# Obje dosyalarını linkleyerek ana çalıştırılabilir dosyayı oluşturur
$(TARGET): $(OBJS)
	@echo "Linking..."
	$(CC) $(OBJS) -o $(TARGET) $(LDFLAGS)

# (Objective-C kuralı kaldırıldı, tüm dosyalar saf C olarak derlenmektedir)

# .c dosyaları için standart C derleme kuralı
%.o: %.c
	@echo "Compiling $< as C..."
	$(CC) $(C_CFLAGS) -c $< -o $@

# Oluşturulan dosyaları temizler
clean:
	@echo "Cleaning up..."
	@rm -rf $(TARGET) $(OBJS) $(APP_BUNDLE)
	@# Eski root dizini objelerini de temizle
	@rm -f *.o ai.o game.o renderer.o main.o Dama DamaOyunu FinalTest TestSDL
	@echo "Done."

# Oyunu çalıştırır
run: all
	@echo "Removing quarantine attribute..."
	@xattr -d com.apple.quarantine $(APP_BUNDLE) || true
	@echo "Running the application in a clean shell environment..."
	@zsh --no-rcs -c "open $(APP_BUNDLE)"
