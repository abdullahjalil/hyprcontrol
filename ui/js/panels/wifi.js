async function loadWifi(container) {
  container.innerHTML = `<h1 class="panel-title">Wi-Fi</h1>`;

  // Toggle group
  const toggleGroup = group();
  let enabled = false;
  const sw = toggle(false, async (v) => {
    await api.post("/api/wifi/toggle", { enabled: v });
    enabled = v;
    netGroup.style.opacity = v ? "1" : "0.4";
    netGroup.style.pointerEvents = v ? "auto" : "none";
  });
  toggleGroup.appendChild(row("Wi-Fi", "Enable wireless networking", sw));
  container.appendChild(toggleGroup);

  // Networks group
  const refreshBtn = btn("↺ Refresh", "btn-ghost btn-sm", () => loadNets());
  const netGroup = group("Available Networks", refreshBtn);
  container.appendChild(netGroup);

  // IP group
  const ipGroup = group("Connection Details");
  const ipRow  = row("IPv4 Address", null, el("span", "row-sub", "—"));
  const gwRow  = row("Gateway",      null, el("span", "row-sub", "—"));
  const dnsRow = row("DNS",          null, el("span", "row-sub", "—"));
  ipGroup.appendChild(ipRow);
  ipGroup.appendChild(gwRow);
  ipGroup.appendChild(dnsRow);
  container.appendChild(ipGroup);

  async function loadNets() {
    // Clear old rows
    netGroup.querySelectorAll(".net-row").forEach(r => r.remove());
    const sp = spinner();
    const loadRow = el("div", "row");
    loadRow.appendChild(el("span", "row-sub", "Scanning…"));
    loadRow.appendChild(sp);
    netGroup.appendChild(loadRow);

    const data = await api.get("/api/wifi/status");
    loadRow.remove();
    enabled = data.enabled;
    sw.querySelector("input").checked = enabled;

    data.networks.forEach(net => {
      const r = el("div", `net-row${net.active ? " connected" : ""}`);

      const sigMap = { 75: "▂▄▆█", 50: "▂▄▆ ", 25: "▂▄  ", 0: "▂   " };
      let sigStr = "▂   ";
      if (net.signal > 75) sigStr = "▂▄▆█";
      else if (net.signal > 50) sigStr = "▂▄▆ ";
      else if (net.signal > 25) sigStr = "▂▄  ";

      r.appendChild(el("span", "signal-icon", sigStr));
      const info = el("div", "net-info");
      info.appendChild(el("div", "net-name", net.ssid));
      info.appendChild(el("div", "net-detail", `${net.security || "Open"} · ${net.signal}%`));
      r.appendChild(info);

      if (net.locked) r.appendChild(el("span", "row-sub", "🔒"));

      if (net.active) {
        r.appendChild(badge("connected", "success"));
      } else {
        r.appendChild(btn("Connect", "btn-ghost btn-sm", () => connectTo(net)));
      }
      netGroup.appendChild(r);
    });

    if (!data.networks.length) {
      netGroup.appendChild(el("div", "empty", "No networks found"));
    }

    const ip = data.ip;
    ipRow.querySelector(".row-sub").textContent  = ip.ip      || "—";
    gwRow.querySelector(".row-sub").textContent  = ip.gateway || "—";
    dnsRow.querySelector(".row-sub").textContent = ip.dns     || "—";
  }

  function connectTo(net) {
    if (net.locked) {
      dialog(
        `Connect to ${net.ssid}`,
        "Enter the network password:",
        async (pw) => {
          toast("Connecting…");
          await api.post("/api/wifi/connect", { ssid: net.ssid, password: pw });
          setTimeout(loadNets, 3000);
        },
        "Connect",
        "Password"
      );
    } else {
      toast("Connecting…");
      api.post("/api/wifi/connect", { ssid: net.ssid }).then(() => {
        setTimeout(loadNets, 2000);
      });
    }
  }

  loadNets();
}
