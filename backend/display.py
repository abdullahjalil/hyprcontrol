"""Display backend — reads from hyprctl, writes to hyprland.conf"""
import subprocess
import json
import re
from hyprcontrol.backend.hyprland import read_conf, CONF_PATH, reload


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
    """Update monitor = line in hyprland.conf."""
    content = read_conf()
    # Parse resolution
    res_str = f"{resolution}@{refresh}"
    scale_str = str(scale)

    pattern = rf"^(monitor\s*=\s*{re.escape(name)}\s*,).*$"
    new_line = f"monitor = {name},{res_str},0x0,{scale_str}"

    if re.search(pattern, content, re.MULTILINE):
        content = re.sub(pattern, new_line, content, flags=re.MULTILINE)
    else:
        content += f"\n{new_line}\n"

    CONF_PATH.write_text(content)
    reload()


def set_vrr(monitor_name: str, state: bool):
    """Set VRR for a monitor via hyprctl."""
    _run(["hyprctl", "keyword", "monitor",
          f"{monitor_name},addreserved,0,0,0,0" if not state else f"{monitor_name},vrr,1"])
