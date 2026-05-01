"""Wi-Fi backend — wraps nmcli"""
import subprocess
import re


def _run(cmd: list) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        return r.stdout.strip()
    except Exception:
        return ""


def is_enabled() -> bool:
    out = _run(["nmcli", "radio", "wifi"])
    return "enabled" in out.lower()


def set_enabled(state: bool):
    _run(["nmcli", "radio", "wifi", "on" if state else "off"])


def get_networks() -> list:
    """Returns list of dicts: ssid, signal, security, active, saved"""
    out = _run([
        "nmcli", "-t", "-f",
        "SSID,SIGNAL,SECURITY,ACTIVE,IN-USE",
        "device", "wifi", "list"
    ])
    networks = []
    seen = set()
    for line in out.splitlines():
        parts = line.split(":")
        if len(parts) < 4:
            continue
        ssid = parts[0].strip()
        if not ssid or ssid in seen:
            continue
        seen.add(ssid)
        try:
            signal = int(parts[1])
        except ValueError:
            signal = 0
        security = parts[2] if len(parts) > 2 else ""
        active   = parts[3].lower() == "yes" if len(parts) > 3 else False
        in_use   = parts[4].lower() == "*"   if len(parts) > 4 else False
        networks.append({
            "ssid":     ssid,
            "signal":   signal,
            "security": security,
            "active":   active or in_use,
            "locked":   bool(security and security != "--"),
        })
    networks.sort(key=lambda n: (-n["active"], -n["signal"]))
    return networks


def get_active_connection() -> dict:
    out = _run([
        "nmcli", "-t", "-f",
        "NAME,TYPE,DEVICE",
        "connection", "show", "--active"
    ])
    for line in out.splitlines():
        parts = line.split(":")
        if len(parts) >= 3 and "wifi" in parts[1].lower():
            return {"name": parts[0], "device": parts[2]}
    return {}


def get_ip_info() -> dict:
    out = _run(["nmcli", "-t", "-f", "IP4.ADDRESS,IP4.GATEWAY,IP4.DNS", "device", "show"])
    info = {"ip": "—", "gateway": "—", "dns": "—"}
    for line in out.splitlines():
        if "IP4.ADDRESS" in line and info["ip"] == "—":
            m = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
            if m:
                info["ip"] = m.group(1)
        elif "IP4.GATEWAY" in line and info["gateway"] == "—":
            m = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
            if m:
                info["gateway"] = m.group(1)
        elif "IP4.DNS" in line and info["dns"] == "—":
            m = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
            if m:
                info["dns"] = m.group(1)
    return info


def connect(ssid: str, password: str = None) -> bool:
    if password:
        r = subprocess.run(
            ["nmcli", "device", "wifi", "connect", ssid, "password", password],
            capture_output=True, text=True, timeout=20
        )
    else:
        r = subprocess.run(
            ["nmcli", "device", "wifi", "connect", ssid],
            capture_output=True, text=True, timeout=20
        )
    return r.returncode == 0


def disconnect() -> bool:
    conn = get_active_connection()
    if conn.get("name"):
        r = subprocess.run(
            ["nmcli", "connection", "down", conn["name"]],
            capture_output=True, text=True, timeout=8
        )
        return r.returncode == 0
    return False
