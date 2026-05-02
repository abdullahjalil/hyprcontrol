"""Appearance backend — GTK theme, icons, cursor, fonts"""
import os
import subprocess
import re
from pathlib import Path

GTK3_SETTINGS = Path.home() / ".config" / "gtk-3.0" / "settings.ini"
GTK4_SETTINGS = Path.home() / ".config" / "gtk-4.0" / "settings.ini"
ICONS_DEFAULT  = Path.home() / ".icons" / "default" / "index.theme"
HYPRLAND_CONF  = Path.home() / ".config" / "hypr" / "hyprland.conf"


def _run(cmd: list) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception:
        return ""


def _read_gtk(path: Path) -> dict:
    settings = {}
    if not path.exists():
        return settings
    for line in path.read_text().splitlines():
        if "=" in line and not line.strip().startswith(("#", "[")):
            k, _, v = line.partition("=")
            settings[k.strip()] = v.strip()
    return settings


def _write_gtk(key: str, value: str):
    for path in [GTK3_SETTINGS, GTK4_SETTINGS]:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            content = path.read_text()
            pattern = rf"^({re.escape(key)}\s*=\s*).*$"
            if re.search(pattern, content, re.MULTILINE):
                content = re.sub(pattern, f"{key} = {value}", content, flags=re.MULTILINE)
            else:
                if "[Settings]" not in content:
                    content = "[Settings]\n" + content
                content += f"\n{key} = {value}"
        else:
            content = f"[Settings]\n{key} = {value}\n"
        path.write_text(content)


# ── GTK Theme ─────────────────────────────────────────────────

def get_gtk_theme() -> str:
    return _read_gtk(GTK3_SETTINGS).get("gtk-theme-name", "Adwaita-dark")


def set_gtk_theme(name: str):
    _write_gtk("gtk-theme-name", name)
    _run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", name])


# ── Icon Theme ────────────────────────────────────────────────

def get_icon_theme() -> str:
    return _read_gtk(GTK3_SETTINGS).get("gtk-icon-theme-name", "Papirus-Dark")


def set_icon_theme(name: str):
    _write_gtk("gtk-icon-theme-name", name)
    _run(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", name])


# ── Cursor Theme ──────────────────────────────────────────────

def get_cursor_theme() -> str:
    # Check Hyprland env first (most reliable under Wayland)
    if HYPRLAND_CONF.exists():
        content = HYPRLAND_CONF.read_text()
        m = re.search(r"env\s*=\s*XCURSOR_THEME\s*,\s*(.+)", content)
        if m:
            return m.group(1).strip()
    # Fall back to GTK settings
    return _read_gtk(GTK3_SETTINGS).get("gtk-cursor-theme-name", "Adwaita")


def set_cursor_theme(name: str):
    # 1. GTK settings files (gtk-3.0 and gtk-4.0)
    _write_gtk("gtk-cursor-theme-name", name)

    # 2. gsettings
    _run(["gsettings", "set", "org.gnome.desktop.interface", "cursor-theme", name])

    # 3. ~/.icons/default/index.theme — XWayland / X11 apps
    ICONS_DEFAULT.parent.mkdir(parents=True, exist_ok=True)
    ICONS_DEFAULT.write_text(f"[Icon Theme]\nInherits={name}\n")

    # 4. Hyprland env — new windows will use the theme
    _run(["hyprctl", "setenv", "XCURSOR_THEME", name])

    # 5. Force Hyprland to re-read cursor theme via keyword (applies live)
    _run(["hyprctl", "keyword", "env", f"XCURSOR_THEME,{name}"])

    # 6. Reload Hyprland so cursor updates on existing windows
    _run(["hyprctl", "reload"])

    # 7. Persist in hyprland.conf
    if HYPRLAND_CONF.exists():
        conf = HYPRLAND_CONF.read_text()
        pattern = r"^(env\s*=\s*XCURSOR_THEME\s*,\s*).*$"
        new_line = f"env = XCURSOR_THEME,{name}"
        if re.search(pattern, conf, re.MULTILINE):
            conf = re.sub(pattern, new_line, conf, flags=re.MULTILINE)
        else:
            conf += f"\n{new_line}\n"
        HYPRLAND_CONF.write_text(conf)

    # 8. Apply to SDDM so login screen cursor matches
    set_sddm_cursor(name)



def get_cursor_size() -> int:
    # Check hyprland env first
    if HYPRLAND_CONF.exists():
        content = HYPRLAND_CONF.read_text()
        m = re.search(r"env\s*=\s*XCURSOR_SIZE\s*,\s*(\d+)", content)
        if m:
            return int(m.group(1))
    try:
        return int(_read_gtk(GTK3_SETTINGS).get("gtk-cursor-theme-size", "24"))
    except ValueError:
        return 24


def set_cursor_size(size: int):
    _write_gtk("gtk-cursor-theme-size", str(size))
    _run(["gsettings", "set", "org.gnome.desktop.interface", "cursor-size", str(size)])
    _run(["hyprctl", "setenv", "XCURSOR_SIZE", str(size)])

    # Persist in hyprland.conf
    if HYPRLAND_CONF.exists():
        content = HYPRLAND_CONF.read_text()
        pattern = r"^(env\s*=\s*XCURSOR_SIZE\s*,\s*).*$"
        new_line = f"env = XCURSOR_SIZE,{size}"
        if re.search(pattern, content, re.MULTILINE):
            content = re.sub(pattern, new_line, content, flags=re.MULTILINE)
        else:
            content += f"\n{new_line}\n"
        HYPRLAND_CONF.write_text(content)


# ── Font ──────────────────────────────────────────────────────

def get_font_name() -> str:
    return _read_gtk(GTK3_SETTINGS).get("gtk-font-name", "Inter 11")


def set_font_name(name: str):
    _write_gtk("gtk-font-name", name)
    _run(["gsettings", "set", "org.gnome.desktop.interface", "font-name", name])


# ── Apply all — fires gsettings + reloads what can be reloaded live ──

def apply_all(gtk_theme: str = None, icon_theme: str = None,
              cursor_theme: str = None, cursor_size: int = None,
              font: str = None):
    if gtk_theme:    set_gtk_theme(gtk_theme)
    if icon_theme:   set_icon_theme(icon_theme)
    if cursor_theme: set_cursor_theme(cursor_theme)
    if cursor_size:  set_cursor_size(cursor_size)
    if font:         set_font_name(font)

    # Signal GTK apps to reload themes via XSettings / dconf
    _run(["gsettings", "set", "org.gnome.desktop.interface",
          "gtk-theme", gtk_theme or get_gtk_theme()])

    # Reload waybar if running (picks up icon theme changes)
    _run(["pkill", "-SIGUSR2", "waybar"])

    # Hyprctl reload for cursor to take effect on new windows
    _run(["hyprctl", "reload"])


# ── Discovery ─────────────────────────────────────────────────

def get_installed_themes() -> list:
    paths = [Path.home() / ".local/share/themes", Path("/usr/share/themes")]
    themes = set(["Adwaita", "Adwaita-dark"])
    for p in paths:
        if p.exists():
            for d in p.iterdir():
                if d.is_dir() and (d / "gtk-3.0").exists():
                    themes.add(d.name)
    return sorted(themes)


def get_installed_icon_themes() -> list:
    paths = [Path.home() / ".local/share/icons", Path("/usr/share/icons")]
    icons = set()
    for p in paths:
        if p.exists():
            for d in p.iterdir():
                if d.is_dir() and (d / "index.theme").exists():
                    icons.add(d.name)
    return sorted(icons) or ["Papirus-Dark", "Adwaita"]


def get_installed_cursor_themes() -> list:
    paths = [
        Path.home() / ".local/share/icons",
        Path.home() / ".icons",
        Path("/usr/share/icons"),
    ]
    cursors = set()
    for p in paths:
        if p.exists():
            for d in p.iterdir():
                if d.is_dir() and (d / "cursors").exists():
                    cursors.add(d.name)
    return sorted(cursors) or ["Adwaita"]




def set_sddm_cursor(name: str, size: int = 24):
    """Apply cursor theme to SDDM login screen."""
    import shutil

    # ── /etc/sddm.conf.d/cursor.conf (preferred, no sudo needed if in group) ──
    sddm_conf_d = Path("/etc/sddm.conf.d")
    cursor_conf  = sddm_conf_d / "cursor.conf"

    conf_content = f"[Theme]\nCursorTheme={name}\nCursorSize={size}\n"

    # Try writing directly first (works if user is in sddm group or wheel with sudo)
    try:
        sddm_conf_d.mkdir(parents=True, exist_ok=True)
        cursor_conf.write_text(conf_content)
        return True
    except PermissionError:
        pass

    # Fall back to pkexec / sudo
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf',
                                     delete=False) as tmp:
        tmp.write(conf_content)
        tmp_path = tmp.name

    # Try pkexec (polkit — pops up auth dialog)
    for escalate in [["pkexec"], ["sudo", "-n"]]:
        try:
            r = subprocess.run(
                escalate + ["bash", "-c",
                    f"mkdir -p /etc/sddm.conf.d && cp {tmp_path} {cursor_conf}"],
                capture_output=True, text=True, timeout=15
            )
            if r.returncode == 0:
                os.unlink(tmp_path)
                return True
        except Exception:
            continue

    os.unlink(tmp_path)

    # Also try the active SDDM theme conf if one is set
    try:
        sddm_main = Path("/etc/sddm.conf")
        if sddm_main.exists():
            sddm_content = sddm_main.read_text()
            # Find current theme
            m = re.search(r"^\s*Current\s*=\s*(.+)$", sddm_content, re.MULTILINE)
            if m:
                theme_name = m.group(1).strip()
                theme_conf = Path(f"/usr/share/sddm/themes/{theme_name}/theme.conf")
                if theme_conf.exists():
                    theme_content = theme_conf.read_text()
                    if "CursorTheme" in theme_content:
                        theme_content = re.sub(
                            r"CursorTheme=.*", f"CursorTheme={name}", theme_content
                        )
                    else:
                        theme_content += f"\nCursorTheme={name}\n"
                    # Needs root — try pkexec
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf',
                                                     delete=False) as tmp:
                        tmp.write(theme_content)
                        tmp_path = tmp.name
                    subprocess.run(
                        ["pkexec", "cp", tmp_path, str(theme_conf)],
                        capture_output=True, timeout=15
                    )
                    import os; os.unlink(tmp_path)
    except Exception:
        pass

    return False
