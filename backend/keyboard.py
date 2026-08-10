"""Keyboard shortcuts + settings — read from the running compositor via hyprctl.

Previously this parsed `bind =` lines out of hyprland.conf. That yields nothing
on a Hyprland 0.55+ Lua config (binds are `hl.bind(...)` calls), so the panel
always fell back to hardcoded defaults. `hyprctl binds -j` reports the live
binds regardless of whether they came from .conf or .lua. The layout/typing
settings below read via `hyprctl getoption` and apply via `hyprctl keyword`,
persisting into the active config's managed block.
"""
import subprocess
import json

from backend import hyprland, hyprconf

# Layout options offered in the UI: (xkb code, friendly label).
LAYOUTS = [
    ("gb", "English (UK)"),
    ("us", "English (US)"),
    ("es", "Spanish"),
    ("fr", "French"),
    ("de", "German"),
]
VARIANTS = [
    ("", "Default"),
    ("colemak", "Colemak"),
    ("dvorak", "Dvorak"),
    ("workman", "Workman"),
]

_CAPS_ESCAPE = "caps:escape"

# X11/Hyprland modifier mask bits.
_MODS = [
    (64, "SUPER"),
    (8,  "ALT"),
    (4,  "CTRL"),
    (1,  "SHIFT"),
]

# Friendlier labels for common dispatchers when a bind has no description.
_DISPATCHER_LABEL = {
    "exec": "Run",
    "killactive": "Close window",
    "fullscreen": "Toggle fullscreen",
    "togglefloating": "Toggle floating",
    "exit": "Exit Hyprland",
    "workspace": "Workspace",
    "movetoworkspace": "Move to workspace",
    "movefocus": "Move focus",
    "movewindow": "Move window",
    "togglesplit": "Toggle split",
    "pseudo": "Pseudo-tile",
}

DEFAULT_SHORTCUTS = [
    {"action": "Launch terminal",   "keys": "SUPER + Return"},
    {"action": "App launcher",      "keys": "SUPER + Space"},
    {"action": "Close window",      "keys": "SUPER + Q"},
    {"action": "Lock screen",       "keys": "SUPER + L"},
    {"action": "Screenshot",        "keys": "SUPER + Shift + S"},
    {"action": "Toggle float",      "keys": "SUPER + F"},
    {"action": "Toggle fullscreen", "keys": "SUPER + M"},
]


def _decode_mods(modmask: int) -> list:
    names = []
    for bit, name in _MODS:
        if modmask & bit:
            names.append(name)
    return names


def _describe(b: dict) -> str:
    desc = (b.get("description") or "").strip()
    if desc:
        return desc
    disp = b.get("dispatcher", "")
    arg = (b.get("arg") or "").strip()
    label = _DISPATCHER_LABEL.get(disp, disp or "Bind")
    if disp == "exec" and arg:
        # Show just the program name, not the whole command line.
        prog = arg.split()[0].split("/")[-1]
        return f"Run {prog}"
    if arg:
        return f"{label} {arg}"
    return label


def get_shortcuts() -> list:
    try:
        out = subprocess.run(
            ["hyprctl", "binds", "-j"],
            capture_output=True, text=True, timeout=5
        ).stdout
        binds = json.loads(out)
    except Exception:
        return DEFAULT_SHORTCUTS

    shortcuts = []
    seen = set()
    for b in binds:
        key = b.get("key", "")
        if not key:
            continue
        mods = _decode_mods(b.get("modmask", 0))
        combo = " + ".join(mods + [key])
        action = _describe(b)
        dedup = (combo, action)
        if dedup in seen:
            continue
        seen.add(dedup)
        shortcuts.append({"action": action, "keys": combo})

    return shortcuts if shortcuts else DEFAULT_SHORTCUTS


# ── Keyboard settings (layout / typing) ───────────────────────

def _kb_options() -> list:
    raw = hyprland.option_str("input:kb_options", "")
    return [o for o in (x.strip() for x in raw.split(",")) if o]


def get_settings() -> dict:
    opts = _kb_options()
    return {
        "layout":       hyprland.option_str("input:kb_layout", "us"),
        "variant":      hyprland.option_str("input:kb_variant", ""),
        "repeat_delay": hyprland.option_int("input:repeat_delay", 600),
        "repeat_rate":  hyprland.option_int("input:repeat_rate", 25),
        "caps_escape":  _CAPS_ESCAPE in opts,
        "numlock":      hyprland.option_int("input:numlock_by_default", 0) == 1,
        "layouts":      LAYOUTS,
        "variants":     VARIANTS,
    }


def set_layout(code: str):
    hyprland.keyword("input:kb_layout", code)
    hyprconf.persist({"kb_layout": code})


def set_variant(code: str):
    hyprland.keyword("input:kb_variant", code)
    hyprconf.persist({"kb_variant": code})


def set_repeat_delay(ms: int):
    hyprland.keyword("input:repeat_delay", int(ms))
    hyprconf.persist({"repeat_delay": int(ms)})


def set_repeat_rate(rate: int):
    hyprland.keyword("input:repeat_rate", int(rate))
    hyprconf.persist({"repeat_rate": int(rate)})


def set_caps_escape(state: bool):
    opts = _kb_options()
    if state and _CAPS_ESCAPE not in opts:
        opts.append(_CAPS_ESCAPE)
    elif not state and _CAPS_ESCAPE in opts:
        opts.remove(_CAPS_ESCAPE)
    value = ",".join(opts)
    hyprland.keyword("input:kb_options", value)
    hyprconf.persist({"kb_options": value})


def set_numlock(state: bool):
    hyprland.keyword("input:numlock_by_default", bool(state))
    hyprconf.persist({"numlock": bool(state)})
