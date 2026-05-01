"""Audio backend — wraps wpctl (PipeWire) with pactl fallback"""
import subprocess
import re


def _run(cmd: list) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception:
        return ""


# ── Volume ────────────────────────────────────────────────────

def get_volume() -> int:
    out = _run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
    m = re.search(r"Volume:\s*([\d.]+)", out)
    if m:
        return min(100, round(float(m.group(1)) * 100))
    return 0


def set_volume(val: int):
    pct = max(0, min(150, val))
    _run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{pct}%"])


def is_muted() -> bool:
    out = _run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
    return "[MUTED]" in out


def set_muted(state: bool):
    _run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "1" if state else "0"])


def toggle_mute():
    _run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])


# ── Microphone ───────────────────────────────────────────────

def get_mic_volume() -> int:
    out = _run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SOURCE@"])
    m = re.search(r"Volume:\s*([\d.]+)", out)
    if m:
        return min(100, round(float(m.group(1)) * 100))
    return 0


def set_mic_volume(val: int):
    pct = max(0, min(100, val))
    _run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SOURCE@", f"{pct}%"])


def is_mic_muted() -> bool:
    out = _run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SOURCE@"])
    return "[MUTED]" in out


def set_mic_muted(state: bool):
    _run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SOURCE@", "1" if state else "0"])


# ── Sinks / sources ──────────────────────────────────────────

def get_sinks() -> list:
    """Return list of (name, description) for output devices."""
    out = _run(["pactl", "list", "short", "sinks"])
    sinks = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            sinks.append(parts[1].strip())
    return sinks if sinks else ["Default Output"]


def get_sources() -> list:
    out = _run(["pactl", "list", "short", "sources"])
    sources = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and "monitor" not in parts[1].lower():
            sources.append(parts[1].strip())
    return sources if sources else ["Default Input"]


def get_default_sink() -> str:
    return _run(["pactl", "get-default-sink"])


def get_default_source() -> str:
    return _run(["pactl", "get-default-source"])


def set_default_sink(name: str):
    _run(["pactl", "set-default-sink", name])


def set_default_source(name: str):
    _run(["pactl", "set-default-source", name])
