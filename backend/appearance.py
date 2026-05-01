"""Appearance backend — GTK theme, icons, cursor, fonts"""
import os
import subprocess
import re
from pathlib import Path


GTK3_SETTINGS = Path.home() / ".config" / "gtk-3.0" / "settings.ini"
GTK4_SETTINGS = Path.home() / ".config" / "gtk-4.0" / "settings.ini"


def _run(cmd: list) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception:
        return ""


def _read_gtk_settings(path: Path) -> dict:
    settings = {}
    if not path.exists():
        return settings
    for line in path.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#") and not line.strip().startswith("["):
            k, _, v = line.partition("=")
            settings[k.strip()] = v.strip()
    return settings


def _write_gtk_setting(key: str, value: str):
    for path in [GTK3_SETTINGS, GTK4_SETTINGS]:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            content = path.read_text()
            pattern = rf"^({re.escape(key)}\s*=\s*).*$"
            if re.search(pattern, content, re.MULTILINE):
                content = re.sub(pattern, rf"{key} = {value}", content, flags=re.MULTILINE)
            else:
                if "[Settings]" not in content:
                    content = "[Settings]\n" + content
                content += f"\n{key} = {value}"
            path.write_text(content)
        else:
            path.write_text(f"[Settings]\n{key} = {value}\n")


def get_gtk_theme() -> str:
    settings = _read_gtk_settings(GTK3_SETTINGS)
    return settings.get("gtk-theme-name", "Adwaita-dark")


def set_gtk_theme(name: str):
    _write_gtk_setting("gtk-theme-name", name)
    _run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", name])


def get_icon_theme() -> str:
    settings = _read_gtk_settings(GTK3_SETTINGS)
    return settings.get("gtk-icon-theme-name", "Papirus-Dark")


def set_icon_theme(name: str):
    _write_gtk_setting("gtk-icon-theme-name", name)
    _run(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", name])


def get_cursor_theme() -> str:
    settings = _read_gtk_settings(GTK3_SETTINGS)
    return settings.get("gtk-cursor-theme-name", "Adwaita")


def set_cursor_theme(name: str):
    _write_gtk_setting("gtk-cursor-theme-name", name)
    _run(["gsettings", "set", "org.gnome.desktop.interface", "cursor-theme", name])


def get_cursor_size() -> int:
    settings = _read_gtk_settings(GTK3_SETTINGS)
    try:
        return int(settings.get("gtk-cursor-theme-size", "24"))
    except ValueError:
        return 24


def set_cursor_size(size: int):
    _write_gtk_setting("gtk-cursor-theme-size", str(size))
    _run(["gsettings", "set", "org.gnome.desktop.interface", "cursor-size", str(size)])


def get_font_name() -> str:
    settings = _read_gtk_settings(GTK3_SETTINGS)
    return settings.get("gtk-font-name", "Inter 11")


def set_font_name(name: str):
    _write_gtk_setting("gtk-font-name", name)
    _run(["gsettings", "set", "org.gnome.desktop.interface", "font-name", name])


def get_installed_themes() -> list:
    paths = [
        Path.home() / ".local" / "share" / "themes",
        Path("/usr/share/themes"),
    ]
    themes = set()
    for p in paths:
        if p.exists():
            for d in p.iterdir():
                if d.is_dir() and (d / "gtk-3.0").exists():
                    themes.add(d.name)
    themes.add("Adwaita")
    themes.add("Adwaita-dark")
    return sorted(themes)


def get_installed_icon_themes() -> list:
    paths = [
        Path.home() / ".local" / "share" / "icons",
        Path("/usr/share/icons"),
    ]
    icons = set()
    for p in paths:
        if p.exists():
            for d in p.iterdir():
                if d.is_dir() and (d / "index.theme").exists():
                    icons.add(d.name)
    return sorted(icons) or ["Papirus-Dark", "Adwaita"]


def get_installed_cursor_themes() -> list:
    paths = [
        Path.home() / ".local" / "share" / "icons",
        Path("/usr/share/icons"),
    ]
    cursors = set()
    for p in paths:
        if p.exists():
            for d in p.iterdir():
                if d.is_dir() and (d / "cursors").exists():
                    cursors.add(d.name)
    return sorted(cursors) or ["Adwaita"]
