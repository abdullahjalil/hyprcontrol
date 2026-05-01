<div align="center">

```
██╗  ██╗██╗   ██╗██████╗ ██████╗  ██████╗ ██████╗ ███╗   ██╗████████╗██████╗  ██████╗ ██╗     
██║  ██║╚██╗ ██╔╝██╔══██╗██╔══██╗██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔═══██╗██║     
███████║ ╚████╔╝ ██████╔╝██████╔╝██║     ██║   ██║██╔██╗ ██║   ██║   ██████╔╝██║   ██║██║     
██╔══██║  ╚██╔╝  ██╔═══╝ ██╔══██╗██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██╗██║   ██║██║     
██║  ██║   ██║   ██║     ██║  ██║╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║╚██████╔╝███████╗
╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
```

**A settings panel for Hyprland — because you deserve better than editing config files by hand.**

[![License](https://img.shields.io/github/license/abdullahjalil/hyprcontrol?color=c95f2e&style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-d4914a?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Arch](https://img.shields.io/badge/arch-linux-1793d1?style=flat-square&logo=archlinux&logoColor=white)](https://archlinux.org)
[![Hyprland](https://img.shields.io/badge/hyprland-compatible-c4a0b8?style=flat-square)](https://hyprland.org)

</div>

---

<div align="center">

*Flask backend · WebKit2GTK window · Desert Dusk palette*

</div>

---

## ⬡ What is this

HyprControl is a GUI control center for Hyprland — inspired by GNOME Settings but built for the tiling workflow. It wraps `nmcli`, `bluetoothctl`, `hyprctl`, `wpctl` and friends behind a clean web-based interface that opens in a native WebKit2 window.

No GTK widget styling fights. No config file spelunking for basic settings. Changes to Hyprland window rules apply **live** via `hyprctl keyword` — you see them instantly.

---

## ◈ Panels

| Panel | Controls |
|-------|----------|
| **Wi-Fi** | Scan networks · connect with password · IP / gateway / DNS info |
| **Bluetooth** | Paired devices · scan nearby · pair / connect / disconnect |
| **Wallpaper** | Browse `~/Pictures` grid · set via hyprpaper · fill mode |
| **Appearance** | GTK theme · icon theme · cursor · font |
| **Display** | Resolution · refresh rate · scale · VRR · rotation |
| **Audio** | Output / input device · volume · mute · PipeWire |
| **Power** | Idle timeouts · lock · suspend · reboot · shutdown |
| **Keyboard** | Layout · repeat delay · Caps→Esc · shortcut reference |
| **Hyprland** | Borders · gaps · blur · animations · layout — **applied live** |

---

## ◈ Requirements

```bash
sudo pacman -S python python-gobject python-flask \
               gtk3 webkit2gtk-4.1 \
               networkmanager bluez bluez-utils
```

> Make sure NetworkManager and bluetooth are running:
> ```bash
> sudo systemctl enable --now NetworkManager bluetooth
> ```

---

## ◈ Install

```bash
git clone https://github.com/abdullahjalil/hyprcontrol
cd hyprcontrol
chmod +x install.sh
./install.sh
```

The installer copies files to `~/.local/share/hyprcontrol`, creates a launcher at `~/.local/bin/hyprcontrol`, and installs a `.desktop` entry so it shows up in your app launcher.

---

## ◈ Usage

```bash
hyprcontrol
```

Add a keybind in `~/.config/hypr/hyprland.conf`:

```ini
bind = SUPER, S, exec, hyprcontrol
```

---

## ◈ How it works

```
┌─────────────────────────────────────────────────────┐
│  WebKit2 GTK3 window                                │
│  ┌───────────────────────────────────────────────┐  │
│  │  localhost:7779  (Flask server)               │  │
│  │                                               │  │
│  │  ui/index.html  ──▶  ui/css/style.css         │  │
│  │                 ──▶  ui/js/panels/*.js        │  │
│  │                       │                       │  │
│  │                       ▼  JSON API             │  │
│  │              server.py  /api/*                │  │
│  │                       │                       │  │
│  │                       ▼                       │  │
│  │         backend/  wifi · bluetooth · audio    │  │
│  │                   display · hyprland · power  │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

- **`main.py`** — launches GTK3 + WebKit2 window; falls back to Chromium `--app` mode or default browser
- **`server.py`** — Flask on `localhost:7779`; serves the UI files and a REST API
- **`backend/`** — thin Python wrappers around system CLI tools
- **`ui/`** — vanilla HTML / CSS / JS, no framework, Desert Dusk palette

---

## ◈ Palette

```
  bg          #1a0f14   deep plum-black
  surface     #221318   cards, sidebar
  accent      #d4914a   amber sand
  terracotta  #c95f2e   errors, destructive actions
  mauve       #c4a0b8   secondary highlights
  sky         #7a8fa0   info, links
  text        #e8ddd0   warm off-white
  muted       #9a8880   secondary text
```

---

## ◈ Troubleshooting

**App does not open a window**
GTK3 + WebKit2 failed — it will fall back to Chromium `--app` mode or your browser. Check terminal output for the URL (`http://localhost:7779`) and open manually.

**Wi-Fi not scanning**
```bash
sudo systemctl start NetworkManager
```

**Bluetooth devices not showing**
```bash
sudo systemctl start bluetooth
```

**Hyprland settings not applying**
Make sure Hyprland is running and `hyprctl` is in your `$PATH`.

---

## ◈ License

MIT © Abdullah Jalil — see [LICENSE](LICENSE)

---

<div align="center">
<sub>built on arch · themed for the desert · made for hyprland</sub>
</div>
