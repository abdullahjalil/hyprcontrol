async function loadBluetooth(container) {
  container.innerHTML = `<h1 class="panel-title">Bluetooth</h1>`;

  const toggleGroup = group();
  const sw = toggle(false, async (v) => {
    await api.post("/api/bluetooth/toggle", { enabled: v });
  });
  toggleGroup.appendChild(row("Bluetooth", "Allow wireless device connections", sw));
  container.appendChild(toggleGroup);

  const scanBtn = btn("Scan", "btn-ghost btn-sm", () => loadDevices());
  const pairedGroup = group("Paired Devices");
  const nearbyGroup = group("Nearby Devices", scanBtn);
  container.appendChild(pairedGroup);
  container.appendChild(nearbyGroup);

  async function loadDevices() {
    pairedGroup.querySelectorAll(".row").forEach(r => r.remove());
    nearbyGroup.querySelectorAll(".row").forEach(r => r.remove());

    const data = await api.get("/api/bluetooth/status");
    sw.querySelector("input").checked = data.enabled;

    const paired   = data.devices.filter(d => d.paired);
    const unpaired = data.devices.filter(d => !d.paired);

    if (!paired.length) {
      pairedGroup.appendChild(el("div", "empty", "No paired devices"));
    } else {
      paired.forEach(d => pairedGroup.appendChild(makeDevRow(d)));
    }

    if (!unpaired.length) {
      nearbyGroup.appendChild(el("div", "empty", "No nearby devices — click Scan"));
    } else {
      unpaired.forEach(d => nearbyGroup.appendChild(makeDevRow(d)));
    }
  }

  function makeDevRow(dev) {
    const iconMap = {
      Headphones: "🎧", Headset: "🎧", Keyboard: "⌨️",
      Mouse: "🖱", Phone: "📱", Computer: "💻"
    };
    const icon = iconMap[dev.type] || "📡";
    const sub = dev.type + (dev.connected ? " · Connected" : "");
    let actionBtn;
    if (dev.paired) {
      actionBtn = dev.connected
        ? btn("Disconnect", "btn-ghost btn-sm", async () => {
            await api.post("/api/bluetooth/disconnect", { mac: dev.mac });
            setTimeout(loadDevices, 1500);
          })
        : btn("Connect", "btn-ghost btn-sm", async () => {
            toast("Connecting…");
            await api.post("/api/bluetooth/connect", { mac: dev.mac });
            setTimeout(loadDevices, 2000);
          });
    } else {
      actionBtn = btn("Pair", "btn-ghost btn-sm", async () => {
        toast("Pairing…");
        await api.post("/api/bluetooth/pair", { mac: dev.mac });
        setTimeout(loadDevices, 3000);
      });
    }
    const nameEl = el("div", "row-left");
    nameEl.appendChild(el("div", "row-label", `${icon}  ${dev.name}`));
    nameEl.appendChild(el("div", "row-sub", sub));
    const r = el("div", "row");
    r.appendChild(nameEl);
    const rr = el("div", "row-right");
    if (dev.connected) rr.appendChild(badge("connected", "success"));
    rr.appendChild(actionBtn);
    r.appendChild(rr);
    return r;
  }

  loadDevices();
}
