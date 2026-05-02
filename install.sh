#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "╔══════════════════════════════════════╗"
echo "║      HyprControl Installer           ║"
echo "╚══════════════════════════════════════╝"
echo ""

echo "→ Installing dependencies..."
sudo pacman -S --needed --noconfirm \
  python python-gobject python-flask \
  gtk3 webkit2gtk-4.1 \
  networkmanager bluez bluez-utils

echo "  ✓ Dependencies installed"

echo "→ Installing app..."
INSTALL_DIR="$HOME/.local/share/hyprcontrol"
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp -r "$SCRIPT_DIR"/{main.py,server.py,backend,ui} "$INSTALL_DIR/"
echo "  ✓ Installed to $INSTALL_DIR"

echo "→ Creating launcher..."
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/hyprcontrol" << LAUNCHER
#!/usr/bin/env bash
exec python3 "$INSTALL_DIR/main.py" "\$@"
LAUNCHER
chmod +x "$HOME/.local/bin/hyprcontrol"
echo "  ✓ Launcher at ~/.local/bin/hyprcontrol"

echo "→ Installing desktop entry..."
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/hyprcontrol.desktop" << DESKTOP
[Desktop Entry]
Name=HyprControl
Comment=Settings panel for Hyprland
Exec=$HOME/.local/bin/hyprcontrol
Icon=preferences-system
Terminal=false
Type=Application
Categories=Settings;System;
Keywords=settings;wifi;bluetooth;display;wallpaper;hyprland;
StartupWMClass=hyprcontrol
DESKTOP
echo "  ✓ Desktop entry installed"

# PATH check
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
  echo ""
  echo "  ⚠  Add to your ~/.zshrc:"
  echo '     export PATH="$HOME/.local/bin:$PATH"'
fi

echo ""
echo "╔══════════════════════════════════════╗"
echo "║           Installation done!         ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Run:  hyprcontrol"
echo ""
echo "Add keybind to hyprland.conf:"
echo "  bind = SUPER, S, exec, hyprcontrol"
