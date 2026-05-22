#!/bin/bash
echo "=== SDL3 Installation Detective ==="
echo

echo "1. Checking common SDL3 installation locations:"
locations=(
    "/usr/local/include/SDL3"
    "/opt/homebrew/include/SDL3"
    "/usr/include/SDL3"
    "/usr/local/Cellar/sdl3"
    "/opt/homebrew/Cellar/sdl3"
    "/opt/homebrew/lib"
    "/usr/local/lib"
)

for loc in "${locations[@]}"; do
    if [ -d "$loc" ]; then
        echo "✓ Found: $loc"
        ls -la "$loc" | head -5
        echo
    else
        echo "✗ Not found: $loc"
    fi
done

echo
echo "2. Searching for SDL3 files system-wide:"
echo "Looking for SDL.h files containing SDL3..."
find /usr /opt 2>/dev/null | grep -i sdl3 | head -10

echo
echo "3. Checking pkg-config for SDL3:"
if command -v pkg-config &> /dev/null; then
    echo "pkg-config found, checking for SDL3..."
    if pkg-config --exists sdl3 2>/dev/null; then
        echo "✓ SDL3 found via pkg-config"
        echo "Include path: $(pkg-config --cflags sdl3)"
        echo "Library path: $(pkg-config --libs sdl3)"
    else
        echo "✗ SDL3 not found via pkg-config"
        echo "Available SDL packages:"
        pkg-config --list-all | grep -i sdl
    fi
else
    echo "pkg-config not found"
fi

echo
echo "4. Checking Homebrew installation:"
if command -v brew &> /dev/null; then
    echo "Homebrew found, checking SDL3 installation..."
    if brew list | grep -i sdl3; then
        echo "✓ SDL3 installed via Homebrew"
        brew --prefix sdl3 2>/dev/null || echo "Could not get SDL3 prefix"
    else
        echo "✗ SDL3 not installed via Homebrew"
        echo "Available SDL packages:"
        brew search sdl
    fi
else
    echo "Homebrew not found"
fi

echo
echo "5. Manual search for any SDL headers:"
echo "Searching for any SDL.h files..."
find /usr /opt 2>/dev/null -name "SDL.h" -type f | head -5

echo
echo "=== End of SDL3 Installation Detective ==="