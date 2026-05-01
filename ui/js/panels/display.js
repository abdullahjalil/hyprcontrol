async function loadDisplay(container) {
  container.innerHTML = `<h1 class="panel-title">Display</h1>`;
  const data = await api.get("/api/display/status");

  if (!data.monitors.length) {
    container.appendChild(el("div", "empty", "No monitors detected. Is Hyprland running?"));
    return;
  }

  data.monitors.forEach(mon => {
    const g = group(`${mon.name}  —  ${mon.description || mon.name}`);
    const resList = [...new Set((mon.modes || []).map(m => m.split("@")[0]))];
    if (!resList.length) resList.push(`${mon.width}x${mon.height}`);
    g.appendChild(row("Resolution", null,
      select(resList, `${mon.width}x${mon.height}`, () => {})));

    const rates = [...new Set((mon.modes || [])
      .filter(m => m.includes("@"))
      .map(m => Math.round(parseFloat(m.split("@")[1])))
    )].sort((a,b) => b-a);
    const rateList = rates.length ? rates.map(r => `${r} Hz`) : [`${mon.refresh} Hz`];
    g.appendChild(row("Refresh Rate", null,
      select(rateList, `${mon.refresh} Hz`, () => {})));

    g.appendChild(row("Scale", null,
      slider(1.0, 2.0, mon.scale, "x", () => {})));

    g.appendChild(row("Rotation", null,
      select(["0° Normal","90° CW","180° Flipped","270° CCW"], "0° Normal", () => {})));

    g.appendChild(row("VRR / Adaptive Sync", null,
      toggle(false, () => {})));

    g.appendChild(row("Night Light", null,
      toggle(false, () => {})));

    const applyBtn = btn("Apply Changes", "btn-accent", () => toast("Display settings applied"));
    const applyWrap = el("div", "");
    applyWrap.style.cssText = "padding:10px 18px 14px";
    applyWrap.appendChild(applyBtn);
    g.appendChild(applyWrap);
    container.appendChild(g);
  });
}
