"""Keyboard shortcuts — reads from hyprland.conf"""
import re
from pathlib import Path

CONF = Path.home() / ".config" / "hypr" / "hyprland.conf"

DEFAULT_SHORTCUTS = [
    {"action": "Launch terminal",      "keys": "SUPER + Return"},
    {"action": "App launcher",         "keys": "SUPER + Space"},
    {"action": "Close window",         "keys": "SUPER + Q"},
    {"action": "Lock screen",          "keys": "SUPER + L"},
    {"action": "Screenshot",           "keys": "SUPER + Shift + S"},
    {"action": "Toggle float",         "keys": "SUPER + F"},
    {"action": "Toggle fullscreen",    "keys": "SUPER + M"},
    {"action": "Next workspace",       "keys": "SUPER + ]"},
    {"action": "Prev workspace",       "keys": "SUPER + ["},
    {"action": "Focus up",             "keys": "SUPER + K"},
    {"action": "Focus down",           "keys": "SUPER + J"},
    {"action": "Focus left",           "keys": "SUPER + H"},
    {"action": "Focus right",          "keys": "SUPER + L"},
    {"action": "Move to workspace 1",  "keys": "SUPER + 1"},
    {"action": "Move to workspace 2",  "keys": "SUPER + 2"},
]


def get_shortcuts() -> list:
    if not CONF.exists():
        return DEFAULT_SHORTCUTS
    content = CONF.read_text()
    shortcuts = []
    for m in re.finditer(r"^bind\s*=\s*(.+)$", content, re.MULTILINE):
        parts = [p.strip() for p in m.group(1).split(",")]
        if len(parts) >= 3:
            mods = parts[0]
            key  = parts[1]
            desc = parts[3] if len(parts) > 3 else parts[2]
            keys = " + ".join(filter(None, [mods, key]))
            shortcuts.append({"action": desc, "keys": keys})
    return shortcuts if shortcuts else DEFAULT_SHORTCUTS
