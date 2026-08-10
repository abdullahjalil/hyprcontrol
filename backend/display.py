"""Display backend — reads from hyprctl, persists format-aware (conf or lua)."""
import subprocess
import json
from backend import hyprconf
from backend.hyprland import reload


def _run(cmd: list) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception:
        return ""


def get_monitors() -> list:
    """Get monitor info from hyprctl."""
    out = _run(["hyprctl", "monitors", "-j"])
    try:
        monitors = json.loads(out)
        result = []
        for m in monitors:
            result.append({
                "name":        m.get("name", ""),
                "description": m.get("description", ""),
                "width":       m.get("width", 1920),
                "height":      m.get("height", 1080),
                "refresh":     round(m.get("refreshRate", 60)),
                "scale":       m.get("scale", 1.0),
                "x":           m.get("x", 0),
                "y":           m.get("y", 0),
                "focused":     m.get("focused", False),
            })
        return result
    except Exception:
        return []


def get_available_modes(monitor_name: str) -> list:
    """Get available resolutions from hyprctl."""
    out = _run(["hyprctl", "monitors", "-j"])
    try:
        monitors = json.loads(out)
        for m in monitors:
            if m.get("name") == monitor_name:
                modes = []
                for mode in m.get("availableModes", []):
                    modes.append(mode)
                return modes
    except Exception:
        pass
    return ["2560x1440@165Hz", "1920x1080@144Hz", "1920x1080@60Hz"]


def set_monitor(name: str, resolution: str, refresh: int, scale: float, transform: int = 0):
    """Apply a monitor change live, then persist it in the active config's format."""
    res_str = f"{resolution}@{refresh}"
    directive = f"{name},{res_str},auto,{scale}"

    # Live apply — works on both .conf and .lua setups.
    _run(["hyprctl", "keyword", "monitor", directive])

    # Persist into our managed 'monitors' block, in the matching syntax.
    fmt = hyprconf.active_format()
    if fmt == "lua":
        body = (
            "hl.monitor({ "
            f'output = "{name}", mode = "{res_str}", '
            f'position = "auto", scale = {scale} }})'
        )
    else:
        body = f"monitor = {directive}"
    hyprconf.write_block("monitors", body)


def set_vrr(monitor_name: str, state: bool):
    """Set VRR for a monitor via hyprctl."""
    _run(["hyprctl", "keyword", "monitor",
          f"{monitor_name},addreserved,0,0,0,0" if not state else f"{monitor_name},vrr,1"])
