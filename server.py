"""
HyprControl Flask server
Serves the HTML UI and provides a JSON API for all system operations
"""
import os
import sys
import json
import subprocess
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend import wifi, bluetooth, audio, display, appearance, power, hyprland, keyboard

app = Flask(__name__, static_folder="ui")
SERVER_PORT = 7779
UI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui")


def start_server():
    app.run(host="127.0.0.1", port=SERVER_PORT, debug=False, use_reloader=False)


# ── Serve UI ──────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(UI_DIR, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(UI_DIR, path)


# ── Wi-Fi ─────────────────────────────────────────────────────
@app.route("/api/wifi/status")
def wifi_status():
    return jsonify({"enabled": wifi.is_enabled(), "networks": wifi.get_networks(),
                    "ip": wifi.get_ip_info()})

@app.route("/api/wifi/toggle", methods=["POST"])
def wifi_toggle():
    state = request.json.get("enabled", True)
    wifi.set_enabled(state)
    return jsonify({"ok": True})

@app.route("/api/wifi/connect", methods=["POST"])
def wifi_connect():
    ssid = request.json.get("ssid")
    password = request.json.get("password")
    ok = wifi.connect(ssid, password)
    return jsonify({"ok": ok})

@app.route("/api/wifi/disconnect", methods=["POST"])
def wifi_disconnect():
    ok = wifi.disconnect()
    return jsonify({"ok": ok})


# ── Bluetooth ─────────────────────────────────────────────────
@app.route("/api/bluetooth/status")
def bt_status():
    return jsonify({"enabled": bluetooth.is_enabled(), "devices": bluetooth.get_devices()})

@app.route("/api/bluetooth/toggle", methods=["POST"])
def bt_toggle():
    bluetooth.set_enabled(request.json.get("enabled", True))
    return jsonify({"ok": True})

@app.route("/api/bluetooth/connect", methods=["POST"])
def bt_connect():
    ok = bluetooth.connect(request.json.get("mac"))
    return jsonify({"ok": ok})

@app.route("/api/bluetooth/disconnect", methods=["POST"])
def bt_disconnect():
    ok = bluetooth.disconnect(request.json.get("mac"))
    return jsonify({"ok": ok})

@app.route("/api/bluetooth/pair", methods=["POST"])
def bt_pair():
    ok = bluetooth.pair(request.json.get("mac"))
    return jsonify({"ok": ok})


# ── Audio ─────────────────────────────────────────────────────
@app.route("/api/audio/status")
def audio_status():
    return jsonify({
        "volume": audio.get_volume(), "muted": audio.is_muted(),
        "mic_volume": audio.get_mic_volume(), "mic_muted": audio.is_mic_muted(),
        "sinks": audio.get_sinks(), "sources": audio.get_sources(),
        "default_sink": audio.get_default_sink(),
        "default_source": audio.get_default_source(),
    })

@app.route("/api/audio/volume", methods=["POST"])
def audio_volume():
    audio.set_volume(request.json.get("value", 50))
    return jsonify({"ok": True})

@app.route("/api/audio/mute", methods=["POST"])
def audio_mute():
    audio.set_muted(request.json.get("muted", False))
    return jsonify({"ok": True})

@app.route("/api/audio/mic_volume", methods=["POST"])
def audio_mic_volume():
    audio.set_mic_volume(request.json.get("value", 80))
    return jsonify({"ok": True})

@app.route("/api/audio/mic_mute", methods=["POST"])
def audio_mic_mute():
    audio.set_mic_muted(request.json.get("muted", False))
    return jsonify({"ok": True})

@app.route("/api/audio/sink", methods=["POST"])
def audio_sink():
    audio.set_default_sink(request.json.get("name"))
    return jsonify({"ok": True})

@app.route("/api/audio/source", methods=["POST"])
def audio_source():
    audio.set_default_source(request.json.get("name"))
    return jsonify({"ok": True})


# ── Display ───────────────────────────────────────────────────
@app.route("/api/display/status")
def display_status():
    monitors = display.get_monitors()
    for m in monitors:
        m["modes"] = display.get_available_modes(m["name"])
    return jsonify({"monitors": monitors})


# ── Appearance ────────────────────────────────────────────────
@app.route("/api/appearance/status")
def appearance_status():
    return jsonify({
        "gtk_theme": appearance.get_gtk_theme(),
        "icon_theme": appearance.get_icon_theme(),
        "cursor_theme": appearance.get_cursor_theme(),
        "cursor_size": appearance.get_cursor_size(),
        "font": appearance.get_font_name(),
        "themes": appearance.get_installed_themes(),
        "icons": appearance.get_installed_icon_themes(),
        "cursors": appearance.get_installed_cursor_themes(),
    })

@app.route("/api/appearance/set", methods=["POST"])
def appearance_set():
    data = request.json
    if "gtk_theme"    in data: appearance.set_gtk_theme(data["gtk_theme"])
    if "icon_theme"   in data: appearance.set_icon_theme(data["icon_theme"])
    if "cursor_theme" in data: appearance.set_cursor_theme(data["cursor_theme"])
    if "cursor_size"  in data: appearance.set_cursor_size(int(data["cursor_size"]))
    return jsonify({"ok": True})

@app.route("/api/appearance/apply", methods=["POST"])
def appearance_apply():
    data = request.json
    appearance.apply_all(
        gtk_theme    = data.get("gtk_theme"),
        icon_theme   = data.get("icon_theme"),
        cursor_theme = data.get("cursor_theme"),
        cursor_size  = int(data["cursor_size"]) if "cursor_size" in data else None,
        font         = data.get("font"),
    )
    return jsonify({"ok": True})



# ── Power ─────────────────────────────────────────────────────
@app.route("/api/power/suspend",   methods=["POST"])
def power_suspend():   power.suspend();   return jsonify({"ok": True})

@app.route("/api/power/reboot",    methods=["POST"])
def power_reboot():    power.reboot();    return jsonify({"ok": True})

@app.route("/api/power/shutdown",  methods=["POST"])
def power_shutdown():  power.shutdown();  return jsonify({"ok": True})

@app.route("/api/power/lock",      methods=["POST"])
def power_lock():      power.lock_screen(); return jsonify({"ok": True})


# ── Hyprland ──────────────────────────────────────────────────
@app.route("/api/hyprland/status")
def hyprland_status():
    return jsonify({
        "border_size":    hyprland.get_border_size(),
        "corner_radius":  hyprland.get_corner_radius(),
        "gaps_out":       hyprland.get_gaps_out(),
        "blur":           hyprland.get_blur_enabled(),
        "animations":     hyprland.get_animations_enabled(),
        "focus_mouse":    hyprland.get_focus_follows_mouse(),
        "layout":         hyprland.get_layout(),
        "config_path":    str(hyprland.get_config_path()),
    })

@app.route("/api/hyprland/set", methods=["POST"])
def hyprland_set():
    data = request.json
    kw_map = {
        "border_size":   "general:border_size",
        "corner_radius": "decoration:rounding",
        "gaps_out":      "general:gaps_out",
        "blur":          "decoration:blur:enabled",
        "animations":    "animations:enabled",
        "focus_mouse":   "input:follow_mouse",
        "layout":        "general:layout",
    }
    for key, kw in kw_map.items():
        if key in data:
            val = str(data[key])
            subprocess.run(["hyprctl", "keyword", kw, val], capture_output=True)
    return jsonify({"ok": True})

@app.route("/api/hyprland/reload", methods=["POST"])
def hyprland_reload():
    hyprland.reload()
    return jsonify({"ok": True})


# ── Wallpaper ─────────────────────────────────────────────────
@app.route("/api/wallpaper/list")
def wallpaper_list():
    dirs = [
        Path.home() / "Pictures",
        Path.home() / "wallpapers",
        Path("/usr/share/wallpapers"),
        Path("/usr/share/backgrounds"),
    ]
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    images = []
    for d in dirs:
        if d.exists():
            for f in sorted(d.rglob("*")):
                if f.suffix.lower() in exts and f.is_file():
                    images.append(str(f))
                    if len(images) >= 60:
                        break
        if len(images) >= 60:
            break
    current = hyprland.get_wallpaper_paths()
    return jsonify({"images": images, "current": current[0] if current else ""})

@app.route("/api/wallpaper/set", methods=["POST"])
def wallpaper_set():
    path = request.json.get("path")
    if path:
        import threading
        threading.Thread(target=lambda: hyprland.set_wallpaper(path), daemon=True).start()
    return jsonify({"ok": True})


# ── Keyboard ──────────────────────────────────────────────────
@app.route("/api/keyboard/shortcuts")
def keyboard_shortcuts():
    shortcuts = keyboard.get_shortcuts()
    return jsonify({"shortcuts": shortcuts})


# ── Serve wallpaper images ────────────────────────────────────
@app.route("/api/wallpaper/serve")
def wallpaper_serve():
    from flask import send_file, abort
    path = request.args.get("path", "")
    p = Path(path)
    if p.exists() and p.is_file():
        return send_file(str(p))
    abort(404)
