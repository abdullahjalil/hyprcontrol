"""Hyprland config backend — reads/writes hyprland.conf and calls hyprctl"""
import subprocess
import os
import re
from pathlib import Path


CONF_PATH = Path.home() / ".config" / "hypr" / "hyprland.conf"
HYPRPAPER_CONF = Path.home() / ".config" / "hypr" / "hyprpaper.conf"


def _run(cmd: list) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception:
        return ""


def hyprctl(cmd: str) -> str:
    return _run(["hyprctl", cmd])


def reload():
    _run(["hyprctl", "reload"])


def get_config_path() -> Path:
    return CONF_PATH


def read_conf() -> str:
    if CONF_PATH.exists():
        return CONF_PATH.read_text()
    return ""


def _set_value(key: str, value: str):
    """Set a simple key = value in hyprland.conf (top-level only)."""
    content = read_conf()
    pattern = rf"^(\s*{re.escape(key)}\s*=\s*).*$"
    new_line = f"{key} = {value}"
    if re.search(pattern, content, re.MULTILINE):
        content = re.sub(pattern, new_line, content, flags=re.MULTILINE)
    else:
        content += f"\n{new_line}\n"
    CONF_PATH.write_text(content)


def _get_value(key: str, default: str = "") -> str:
    content = read_conf()
    m = re.search(rf"^\s*{re.escape(key)}\s*=\s*(.+)$", content, re.MULTILINE)
    return m.group(1).strip() if m else default


def _set_in_section(section: str, key: str, value: str):
    """Set key = value inside a section block like 'decoration {}'."""
    content = read_conf()
    pattern = rf"({re.escape(section)}\s*\{{[^}}]*?){re.escape(key)}\s*=\s*[^\n]+"
    replacement = rf"\g<1>{key} = {value}"
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        # Add key inside section if it exists
        section_pattern = rf"({re.escape(section)}\s*\{{)"
        if re.search(section_pattern, content):
            content = re.sub(section_pattern, rf"\1\n    {key} = {value}", content)
    CONF_PATH.write_text(content)


def _get_in_section(section: str, key: str, default: str = "") -> str:
    content = read_conf()
    m = re.search(
        rf"{re.escape(section)}\s*\{{[^}}]*?{re.escape(key)}\s*=\s*([^\n]+)",
        content, re.DOTALL
    )
    return m.group(1).strip() if m else default


# ── Window decorations ────────────────────────────────────────

def get_border_size() -> int:
    return int(_get_in_section("general", "border_size", "1"))

def set_border_size(val: int):
    _set_in_section("general", "border_size", str(val))

def get_gaps_in() -> int:
    return int(_get_in_section("general", "gaps_in", "4"))

def set_gaps_in(val: int):
    _set_in_section("general", "gaps_in", str(val))

def get_gaps_out() -> int:
    return int(_get_in_section("general", "gaps_out", "8"))

def set_gaps_out(val: int):
    _set_in_section("general", "gaps_out", str(val))

def get_corner_radius() -> int:
    return int(_get_in_section("decoration", "rounding", "10"))

def set_corner_radius(val: int):
    _set_in_section("decoration", "rounding", str(val))

def get_blur_enabled() -> bool:
    val = _get_in_section("decoration", "blur", "")
    return "enabled = true" in val or _get_in_section("blur", "enabled", "false") == "true"

def set_blur_enabled(state: bool):
    _set_in_section("blur", "enabled", "true" if state else "false")

def get_active_border_color() -> str:
    return _get_in_section("general", "col.active_border", "rgba(d4914aff)")

def set_active_border_color(color: str):
    _set_in_section("general", "col.active_border", color)

# ── Animations ────────────────────────────────────────────────

def get_animations_enabled() -> bool:
    val = _get_in_section("animations", "enabled", "true")
    return val.lower() == "true" or val == "1"

def set_animations_enabled(state: bool):
    _set_in_section("animations", "enabled", "true" if state else "false")

# ── Input / focus ─────────────────────────────────────────────

def get_focus_follows_mouse() -> bool:
    val = _get_in_section("input", "follow_mouse", "1")
    return val in ("1", "true", "2")

def set_focus_follows_mouse(state: bool):
    _set_in_section("input", "follow_mouse", "1" if state else "0")

def get_touchpad_enabled() -> bool:
    return _get_in_section("touchpad", "natural_scroll", "false").lower() != "false"

def set_touchpad_natural_scroll(state: bool):
    _set_in_section("touchpad", "natural_scroll", "true" if state else "false")

# ── Layout ────────────────────────────────────────────────────

def get_layout() -> str:
    return _get_in_section("general", "layout", "dwindle")

def set_layout(layout: str):
    _set_in_section("general", "layout", layout)

# ── Monitors ─────────────────────────────────────────────────

def get_monitors() -> list:
    """Parse monitor = lines from config."""
    content = read_conf()
    monitors = []
    for m in re.finditer(r"^monitor\s*=\s*(.+)$", content, re.MULTILINE):
        parts = [p.strip() for p in m.group(1).split(",")]
        if len(parts) >= 3:
            monitors.append({
                "name":      parts[0],
                "res":       parts[1] if len(parts) > 1 else "",
                "pos":       parts[2] if len(parts) > 2 else "0x0",
                "scale":     parts[3] if len(parts) > 3 else "1",
            })
    return monitors

# ── Wallpaper ─────────────────────────────────────────────────

def get_wallpaper_paths() -> list:
    if not HYPRPAPER_CONF.exists():
        return []
    content = HYPRPAPER_CONF.read_text()
    paths = re.findall(r"wallpaper\s*=\s*[^,]+,\s*(.+)", content)
    return [p.strip() for p in paths]


def set_wallpaper(path: str):
    """Update hyprpaper.conf and reload hyprpaper."""
    abs_path = str(Path(path).expanduser().resolve())
    content = f"preload = {abs_path}\n"
    # Apply to all monitors
    monitors = get_monitors()
    if monitors:
        for m in monitors:
            content += f"wallpaper = {m['name']},{abs_path}\n"
    else:
        content += f"wallpaper = ,{abs_path}\n"
    HYPRPAPER_CONF.write_text(content)
    # Reload hyprpaper
    subprocess.Popen(["pkill", "hyprpaper"])
    import time
    time.sleep(0.3)
    subprocess.Popen(["hyprpaper"])
