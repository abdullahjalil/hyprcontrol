"""
hyprconf — config-format detection + a managed-block writer.

Hyprland 0.55+ deprecated the old hyprlang `.conf` format in favour of a Lua
config at ~/.config/hypr/hyprland.lua. The important rule (from the Hyprland
wiki): the choice is made ONCE at startup — if hyprland.lua exists it is the
config and any hyprland.conf beside it is ignored silently. So HyprControl must
know which file is actually live, and must write in the matching syntax.

This module centralises that so every backend agrees on the same path/format.
"""
import os
import re
import json
from pathlib import Path


def _config_dir() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "hypr"


CONFIG_DIR = _config_dir()
LUA_PATH = CONFIG_DIR / "hyprland.lua"
CONF_PATH = CONFIG_DIR / "hyprland.conf"

# Delimiters for the block HyprControl owns. We only ever touch text between
# these markers, so the user's hand-written config is never rewritten.
_BEGIN = "hyprcontrol (managed) — do not edit by hand"
_END = "end hyprcontrol (managed)"


def detect() -> tuple[Path, str]:
    """
    Return (path, format) for the *active* config.

    Mirrors Hyprland's own resolution order: lua wins if present, else conf.
    If neither exists we assume lua, since that's what a fresh 0.55+ install
    generates.
    """
    if LUA_PATH.exists():
        return LUA_PATH, "lua"
    if CONF_PATH.exists():
        return CONF_PATH, "conf"
    return LUA_PATH, "lua"


def active_path() -> Path:
    return detect()[0]


def active_format() -> str:
    return detect()[1]


def read() -> str:
    p = active_path()
    return p.read_text() if p.exists() else ""


# ── Managed block ─────────────────────────────────────────────────────────
#
# Persistence strategy that is safe for BOTH formats: append (or replace) a
# single delimited block at the end of the active config. Hyprland applies
# later values last, so an appended override reliably wins over an earlier
# hand-written value without us having to parse or mutate the user's own code.

def _managed_block(settings: dict, fmt: str) -> str:
    """Render the managed block for the given settings dict."""
    # key -> (section path, kind) where kind is int/bool/str
    spec = {
        "border_size":   (("general", "border_size"), "int"),
        "gaps_in":       (("general", "gaps_in"), "int"),
        "gaps_out":      (("general", "gaps_out"), "int"),
        "corner_radius": (("decoration", "rounding"), "int"),
        "blur":          (("decoration", "blur", "enabled"), "bool"),
        "animations":    (("animations", "enabled"), "bool"),
        "focus_mouse":   (("input", "follow_mouse"), "focus"),
        "layout":        (("general", "layout"), "str"),
        # keyboard
        "kb_layout":     (("input", "kb_layout"), "str"),
        "kb_variant":    (("input", "kb_variant"), "str"),
        "kb_options":    (("input", "kb_options"), "str"),
        "repeat_delay":  (("input", "repeat_delay"), "int"),
        "repeat_rate":   (("input", "repeat_rate"), "int"),
        "numlock":       (("input", "numlock_by_default"), "bool"),
        # touchpad
        "natural_scroll":       (("input", "touchpad", "natural_scroll"), "bool"),
        "disable_while_typing": (("input", "touchpad", "disable_while_typing"), "bool"),
    }

    # Build a nested tree so Lua output can group by section.
    tree: dict = {}
    flat: list = []  # (colon_key, value_str) for conf
    for key, val in settings.items():
        if key not in spec:
            continue
        path, kind = spec[key]
        if kind == "bool":
            out = "true" if val else "false"
            lua_val = "true" if val else "false"
        elif kind == "focus":
            out = "1" if val else "0"
            lua_val = "1" if val else "0"
        elif kind == "int":
            out = str(int(val))
            lua_val = str(int(val))
        else:  # str
            out = str(val)
            lua_val = f'"{val}"'
        flat.append((":".join(path), out))
        node = tree
        for part in path[:-1]:
            node = node.setdefault(part, {})
        node[path[-1]] = lua_val

    if fmt == "lua":
        def render(node, indent):
            pad = "    " * indent
            lines = []
            for k, v in node.items():
                if isinstance(v, dict):
                    lines.append(f"{pad}{k} = {{")
                    lines.extend(render(v, indent + 1))
                    lines.append(f"{pad}}},")
                else:
                    lines.append(f"{pad}{k} = {v},")
            return lines
        inner = "\n".join(render(tree, 1))
        return f"hl.config({{\n{inner}\n}})"
    else:
        return "\n".join(f"{ck} = {v}" for ck, v in flat)


def write_block(block_id: str, body: str) -> Path:
    """
    Write `body` into a delimited, idempotent managed block identified by
    `block_id` in the active config, creating the file/dir if needed. An
    existing block with the same id is replaced, not duplicated. The comment
    style matches the active format. Returns the path written.
    """
    path, fmt = detect()
    comment = "--" if fmt == "lua" else "#"
    begin = f"{_BEGIN}: {block_id}"
    end = f"{_END}: {block_id}"

    block = f"{comment} >>> {begin} >>>\n{body.rstrip()}\n{comment} <<< {end} <<<\n"

    path.parent.mkdir(parents=True, exist_ok=True)
    content = path.read_text() if path.exists() else ""

    # Match either comment style so a block written under the other format
    # (e.g. after a conf->lua migration) is still found and replaced.
    marker = re.compile(
        r"(?:^|\n)[ \t]*(?:#|--) >>> " + re.escape(begin) + r".*?"
        + re.escape(end) + r" <<<[ \t]*(?:\n|$)",
        re.DOTALL,
    )
    if marker.search(content):
        content = marker.sub("\n" + block, content)
    else:
        if content and not content.endswith("\n"):
            content += "\n"
        content += "\n" + block
    path.write_text(content)
    return path


_STATE_TAG = "hyprcontrol-state:"


def _read_state() -> dict:
    """Recover previously-persisted settings from the managed block's state line."""
    content = read()
    m = re.search(_STATE_TAG + r"\s*(\{.*\})", content)
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except Exception:
        return {}


def persist(settings: dict) -> Path:
    """
    Persist decoration/input/layout settings into the managed 'settings' block
    of the active config, in the matching syntax. Accumulative: settings from
    earlier calls are preserved and merged, so setting one key at a time never
    wipes the others.
    """
    fmt = active_format()
    merged = {**_read_state(), **settings}
    comment = "--" if fmt == "lua" else "#"
    state_line = f"{comment} {_STATE_TAG} {json.dumps(merged, separators=(',', ':'))}"
    body = state_line + "\n" + _managed_block(merged, fmt)
    return write_block("settings", body)
