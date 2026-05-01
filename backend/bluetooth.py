"""Bluetooth backend — wraps bluetoothctl"""
import subprocess
import re


def _run(cmd: list) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        return r.stdout.strip()
    except Exception:
        return ""


def _bluetoothctl(commands: list) -> str:
    """Send commands to bluetoothctl interactively."""
    input_str = "\n".join(commands) + "\n"
    try:
        r = subprocess.run(
            ["bluetoothctl"],
            input=input_str,
            capture_output=True, text=True, timeout=10
        )
        return r.stdout
    except Exception:
        return ""


def is_enabled() -> bool:
    out = _run(["bluetoothctl", "show"])
    for line in out.splitlines():
        if "Powered:" in line:
            return "yes" in line.lower()
    return False


def set_enabled(state: bool):
    _bluetoothctl([f"power {'on' if state else 'off'}"])


def get_devices() -> list:
    """Returns all known devices."""
    out = _bluetoothctl(["devices", "quit"])
    devices = []
    for line in out.splitlines():
        m = re.match(r"Device\s+([0-9A-F:]+)\s+(.+)", line.strip())
        if m:
            mac, name = m.group(1), m.group(2)
            info = _get_device_info(mac)
            devices.append({
                "mac":       mac,
                "name":      name,
                "connected": info.get("connected", False),
                "paired":    info.get("paired", False),
                "type":      info.get("type", "Unknown"),
            })
    return devices


def _get_device_info(mac: str) -> dict:
    out = _bluetoothctl([f"info {mac}", "quit"])
    info = {"connected": False, "paired": False, "type": "Unknown"}
    for line in out.splitlines():
        if "Connected: yes" in line:
            info["connected"] = True
        elif "Paired: yes" in line:
            info["paired"] = True
        elif "Icon:" in line:
            icon = line.split("Icon:")[-1].strip()
            type_map = {
                "audio-headset":    "Headset",
                "audio-headphones": "Headphones",
                "input-keyboard":   "Keyboard",
                "input-mouse":      "Mouse",
                "phone":            "Phone",
                "computer":         "Computer",
            }
            info["type"] = type_map.get(icon, "Device")
    return info


def connect(mac: str) -> bool:
    out = _bluetoothctl([f"connect {mac}", "quit"])
    return "Connection successful" in out or "Connected: yes" in out


def disconnect(mac: str) -> bool:
    out = _bluetoothctl([f"disconnect {mac}", "quit"])
    return "Successful disconnected" in out or "Connected: no" in out


def pair(mac: str) -> bool:
    out = _bluetoothctl([f"pair {mac}", "quit"])
    return "Pairing successful" in out


def remove(mac: str) -> bool:
    out = _bluetoothctl([f"remove {mac}", "quit"])
    return "Device has been removed" in out
