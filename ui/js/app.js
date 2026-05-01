// app.js — navigation and panel loading

const panels = {
  wifi:       loadWifi,
  bluetooth:  loadBluetooth,
  wallpaper:  loadWallpaper,
  appearance: loadAppearance,
  display:    loadDisplay,
  audio:      loadAudio,
  power:      loadPower,
  keyboard:   loadKeyboard,
  hyprland:   loadHyprland,
};

let currentPanel = null;

function showPanel(name) {
  // Update nav
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  document.querySelector(`[data-panel="${name}"]`).classList.add("active");

  // Update content
  document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
  const panelEl = document.getElementById(`panel-${name}`);
  panelEl.classList.add("active");

  // Load panel data
  if (panels[name]) panels[name](panelEl);
  currentPanel = name;
}

// Nav click handlers
document.querySelectorAll(".nav-item").forEach(item => {
  item.addEventListener("click", () => showPanel(item.dataset.panel));
});

// Boot — load first panel
showPanel("wifi");
