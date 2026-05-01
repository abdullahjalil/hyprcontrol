#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "╔══════════════════════════════════════╗"
echo "║     HyprControl 2 Installer          ║"
echo "╚══════════════════════════════════════╝"
echo ""

echo "→ Installing dependencies..."
sudo pacman -S --needed --noconfirm \
  python python-gobject python-flask gtk4 \
  webkit2gtk-4.1 python-flask networkmanager bluez bluez-utils

echo "  ✓ Done"

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
StartupWMClass=hyprcontrol
DESKTOP

echo ""
echo "╔══════════════════════════════════════╗"
echo "║           All done!                  ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Run:  hyprcontrol"
echo "Test: python3 $INSTALL_DIR/main.py"
echo ""
echo "Add keybind to hyprland.conf:"
echo "  bind = SUPER, S, exec, hyprcontrol"
