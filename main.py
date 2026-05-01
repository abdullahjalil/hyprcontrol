#!/usr/bin/env python3
"""
HyprControl 2 — opens in your browser or a minimal window
"""
import sys
import os
import threading
import time
import subprocess
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import start_server, SERVER_PORT

URL = f"http://localhost:{SERVER_PORT}"


def open_window():
    """Try a standalone WebView window, fall back to browser."""
    # Option 1: GTK3 + WebKit2 4.1 (most common on Arch)
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        gi.require_version("WebKit2", "4.1")
        from gi.repository import Gtk, WebKit2, GLib

        win = Gtk.Window()
        win.set_title("HyprControl")
        win.set_default_size(1100, 700)
        win.connect("destroy", Gtk.main_quit)

        webview = WebKit2.WebView()
        win.add(webview)
        win.show_all()

        def load(_):
            webview.load_uri(URL)
            return False

        GLib.timeout_add(500, load, None)
        Gtk.main()
        return

    except Exception as e:
        print(f"GTK3 WebKit window failed: {e}", file=sys.stderr)

    # Option 2: try opening in a minimal browser window
    for browser_cmd in [
        ["chromium", f"--app={URL}", "--window-size=1100,700",
         "--no-default-browser-check", "--no-first-run"],
        ["firefox", f"--new-window", URL],
        ["xdg-open", URL],
    ]:
        try:
            if subprocess.run(["which", browser_cmd[0]],
                              capture_output=True).returncode == 0:
                subprocess.Popen(browser_cmd)
                # Keep server alive
                while True:
                    time.sleep(1)
                return
        except Exception:
            continue

    # Last resort
    webbrowser.open(URL)
    while True:
        time.sleep(1)


def main():
    # Start Flask server
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(0.5)
    print(f"HyprControl running at {URL}")
    open_window()


if __name__ == "__main__":
    main()
