"""Hyprland backend — reads live state via hyprctl, persists format-aware.

Historically this module parsed ~/.config/hypr/hyprland.conf with regexes.
That breaks on Hyprland 0.55+, where the config may be Lua (hyprland.lua) and
the old .conf is ignored. So reads now go through `hyprctl getoption`, which
reports the live runtime value regardless of config format, and writes go
through hyprconf.persist(), which emits the correct syntax for whichever file
is active. Live tweaks still apply instantly via `hyprctl keyword` (see
server.py); persistence is a separate, explicit step.
"""
import subprocess
import json
import re
from pathlib import Path

from backend import hyprconf

CONF_PATH = hyprconf.CONF_PATH  # kept for backwards compat with importers
HYPRPAPER_CONF = hyprconf.CONFIG_DIR / "hyprpaper.conf"


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
    return hyprconf.active_path()


def get_config_format() -> str:
    return hyprconf.active_format()


def read_conf() -> str:
    return hyprconf.read()


# -- Reading options via hyprctl (format-agnostic) -------------------------
#
# `hyprctl getoption <opt> -j` returns e.g.
#   {"option":"general:border_size","int":2,"float":0.0,"str":"","set":true}
# We pull the field that matches the option's type. This reflects the live
# value whether the source was hyprland.conf or hyprland.lua.

def _getoption(option: str):
    out = _run(["hyprctl", "getoption", option, "-j"])
    if not out:
        return None
    try:
        return json.loads(out)
    except Exception:
        return None


def _opt_int(option: str, default: int) -> int:
    d = _getoption(option)
    if d is not None and "int" in d:
        try:
            return int(d["int"])
        except (TypeError, ValueError):
            pass
    return default


def _opt_str(option: str, default: str) -> str:
    d = _getoption(option)
    if d is not None:
        s = d.get("str", "")
        if s:
            return str(s).strip()
    return default


# Public wrappers so other backends (e.g. keyboard) can read options too.
def option_int(option: str, default: int = 0) -> int:
    return _opt_int(option, default)

def option_str(option: str, default: str = "") -> str:
    return _opt_str(option, default)

def keyword(option: str, value) -> None:
    if isinstance(value, bool):
        value = "true" if value else "false"
    _run(["hyprctl", "keyword", option, str(value)])


# -- Window decorations ----------------------------------------
def get_border_size() -> int:
    return _opt_int("general:border_size", 1)

def set_border_size(val: int):
    _apply_and_persist("border_size", int(val))

def get_gaps_in() -> int:
    return _opt_int("general:gaps_in", 4)

def set_gaps_in(val: int):
    _apply_and_persist("gaps_in", int(val))

def get_gaps_out() -> int:
    return _opt_int("general:gaps_out", 8)

def set_gaps_out(val: int):
    _apply_and_persist("gaps_out", int(val))

def get_corner_radius() -> int:
    return _opt_int("decoration:rounding", 10)

def set_corner_radius(val: int):
    _apply_and_persist("corner_radius", int(val))

def get_blur_enabled() -> bool:
    return _opt_int("decoration:blur:enabled", 1) == 1

def set_blur_enabled(state: bool):
    _apply_and_persist("blur", bool(state))

def get_active_border_color() -> str:
    # Colours/gradients don't round-trip cleanly through getoption, so fall
    # back to the file for this one. Not shown in the status payload.
    d = _getoption("general:col.active_border")
    if d:
        for k in ("str", "data", "custom"):
            if d.get(k):
                return str(d[k]).strip()
    return "rgba(d4914aff)"

def set_active_border_color(color: str):
    _run(["hyprctl", "keyword", "general:col.active_border", color])


# -- Animations ------------------------------------------------
def get_animations_enabled() -> bool:
    return _opt_int("animations:enabled", 1) == 1

def set_animations_enabled(state: bool):
    _apply_and_persist("animations", bool(state))


# -- Input / focus ---------------------------------------------
def get_focus_follows_mouse() -> bool:
    return _opt_int("input:follow_mouse", 1) in (1, 2)

def set_focus_follows_mouse(state: bool):
    _apply_and_persist("focus_mouse", bool(state))

def get_touchpad_natural_scroll() -> bool:
    return _opt_int("input:touchpad:natural_scroll", 0) == 1

def set_touchpad_natural_scroll(state: bool):
    _apply_and_persist("natural_scroll", bool(state))

def get_disable_while_typing() -> bool:
    return _opt_int("input:touchpad:disable_while_typing", 1) == 1

def set_disable_while_typing(state: bool):
    _apply_and_persist("disable_while_typing", bool(state))


# -- Layout ----------------------------------------------------
def get_layout() -> str:
    return _opt_str("general:layout", "dwindle")

def set_layout(layout: str):
    _apply_and_persist("layout", layout)


# -- live-apply + persist helper -------------------------------
_KEYWORD_MAP = {
    "border_size":   "general:border_size",
    "gaps_in":       "general:gaps_in",
    "gaps_out":      "general:gaps_out",
    "corner_radius": "decoration:rounding",
    "blur":          "decoration:blur:enabled",
    "animations":    "animations:enabled",
    "focus_mouse":   "input:follow_mouse",
    "layout":        "general:layout",
    "natural_scroll":       "input:touchpad:natural_scroll",
    "disable_while_typing": "input:touchpad:disable_while_typing",
}


def apply_live(key: str, value) -> None:
    """Apply a single setting to the running compositor (no persistence)."""
    kw = _KEYWORD_MAP.get(key)
    if not kw:
        return
    if key == "focus_mouse":
        value = "1" if value else "0"        # follow_mouse is an int (0-3)
    elif isinstance(value, bool):
        value = "true" if value else "false"
    _run(["hyprctl", "keyword", kw, str(value)])


def _apply_and_persist(key: str, value) -> None:
    apply_live(key, value)
    hyprconf.persist({key: value})


def persist_settings(settings: dict) -> str:
    """Persist a batch of settings to the active config's managed block."""
    path = hyprconf.persist(settings)
    return str(path)


# -- Animations: speed + bezier ------------------------------------------
#
# There's no single "global animation speed" option, so we drive the `global`
# animation leaf with a named bezier. Curve control points below are applied
# under an "hc_"-prefixed name so we never clobber a user's own beziers.

_CURVES = {
    "linear":       "0.0, 0.0, 1.0, 1.0",
    "easeInOut":    "0.65, 0.05, 0.36, 1.0",
    "easeOutQuint": "0.23, 1.0, 0.32, 1.0",
    "overshot":     "0.34, 1.3, 0.64, 1.0",
    "bounce":       "0.5, 1.6, 0.5, 1.0",
}
_DEFAULT_CURVE = "easeOutQuint"


def set_animation(speed: int, bezier: str):
    """Apply a global animation speed + bezier live, then persist."""
    speed = max(1, min(int(speed), 100))
    if bezier not in _CURVES:
        bezier = _DEFAULT_CURVE
    points = _CURVES[bezier]
    name = f"hc_{bezier}"

    # Live apply: define the curve, then point the global leaf at it.
    _run(["hyprctl", "keyword", "bezier", f"{name}, {points}"])
    _run(["hyprctl", "keyword", "animation", f"global, 1, {speed}, {name}"])

    _persist_animation(speed, bezier)


def _persist_animation(speed: int, bezier: str):
    points = _CURVES.get(bezier, _CURVES[_DEFAULT_CURVE])
    name = f"hc_{bezier}"
    fmt = hyprconf.active_format()
    if fmt == "lua":
        pts = ", ".join(
            "{%s, %s}" % (p.strip(), q.strip())
            for p, q in [points.split(",")[0:2], points.split(",")[2:4]]
        )
        body = (
            f'hl.curve("{name}", {{ type = "bezier", points = {{ {pts} }} }})\n'
            f'hl.animation({{ leaf = "global", enabled = true, '
            f'speed = {speed}, bezier = "{name}" }})'
        )
    else:
        body = (
            f"bezier = {name}, {points}\n"
            f"animation = global, 1, {speed}, {name}"
        )
    hyprconf.write_block("animations", body)


def get_animation_settings() -> dict:
    """Read speed/bezier back from our managed block, else defaults."""
    content = hyprconf.read()
    speed, bezier = 5, "overshot"
    m = re.search(r"hc_([a-zA-Z]+)", content)
    if m and m.group(1) in _CURVES:
        bezier = m.group(1)
    m = re.search(r"global,\s*1,\s*(\d+)", content) or \
        re.search(r'leaf\s*=\s*"global".*?speed\s*=\s*(\d+)', content, re.DOTALL)
    if m:
        speed = int(m.group(1))
    return {"speed": speed, "bezier": bezier, "curves": list(_CURVES.keys())}


# -- Monitors (from hyprctl, not the config file) -------------
def get_monitors() -> list:
    out = _run(["hyprctl", "monitors", "-j"])
    try:
        monitors = json.loads(out)
    except Exception:
        return []
    result = []
    for m in monitors:
        result.append({
            "name":  m.get("name", ""),
            "res":   f'{m.get("width", 0)}x{m.get("height", 0)}@{round(m.get("refreshRate", 60))}',
            "pos":   f'{m.get("x", 0)}x{m.get("y", 0)}',
            "scale": str(m.get("scale", 1)),
        })
    return result


# -- Wallpaper (hyprpaper still uses hyprlang) ----------------
def get_wallpaper_paths() -> list:
    """Read path = lines from block-format hyprpaper.conf."""
    if not HYPRPAPER_CONF.exists():
        return []
    content = HYPRPAPER_CONF.read_text()
    paths = re.findall(r"^\s*path\s*=\s*(.+)$", content, re.MULTILINE)
    result = []
    for p in paths:
        p = p.strip()
        if p:
            result.append(str(Path(p).expanduser()))
    return result


def set_wallpaper(path: str):
    """Write block-format hyprpaper.conf and apply via socket."""
    import time

    abs_path = str(Path(path).expanduser().resolve())

    monitor_names = []
    try:
        r = subprocess.run(
            ["hyprctl", "monitors", "-j"],
            capture_output=True, text=True, timeout=5
        )
        monitors = json.loads(r.stdout)
        monitor_names = [m["name"] for m in monitors]
    except Exception:
        pass

    lines = []
    for mon in monitor_names:
        lines.append("wallpaper {")
        lines.append(f"    monitor = {mon}")
        lines.append(f"    path = {abs_path}")
        lines.append("    fit_mode = cover")
        lines.append("}")
        lines.append("")

    lines.append("wallpaper {")
    lines.append("    monitor = ")
    lines.append(f"    path = {abs_path}")
    lines.append("    fit_mode = cover")
    lines.append("}")
    lines.append("")

    HYPRPAPER_CONF.write_text("\n".join(lines))

    socket_ok = False
    try:
        r = subprocess.run(
            ["hyprctl", "hyprpaper", "preload", abs_path],
            capture_output=True, text=True, timeout=5
        )
        if r.returncode == 0:
            for mon in (monitor_names or [""]):
                wp_arg = f"{mon},{abs_path}" if mon else abs_path
                subprocess.run(
                    ["hyprctl", "hyprpaper", "wallpaper", wp_arg],
                    capture_output=True, text=True, timeout=5
                )
            socket_ok = True
    except Exception:
        pass

    if not socket_ok:
        subprocess.run(["pkill", "hyprpaper"], capture_output=True)
        time.sleep(0.5)
        subprocess.Popen(
            ["hyprpaper"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
