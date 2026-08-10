async function loadKeyboard(container) {
  container.innerHTML = `<h1 class="panel-title">Keyboard</h1>`;

  const s = await api.get("/api/keyboard/status");

  // label <-> code maps from backend-provided lists
  const layouts  = s.layouts  || [["us", "English (US)"]];
  const variants = s.variants || [["", "Default"]];
  const layoutLabels  = layouts.map(([, label]) => label);
  const variantLabels = variants.map(([, label]) => label);
  const labelToLayout  = Object.fromEntries(layouts.map(([c, l]) => [l, c]));
  const labelToVariant = Object.fromEntries(variants.map(([c, l]) => [l, c]));
  const layoutToLabel  = Object.fromEntries(layouts.map(([c, l]) => [c, l]));
  const variantToLabel = Object.fromEntries(variants.map(([c, l]) => [c, l]));

  // trailing debounce so dragging a slider doesn't spam the backend / config
  function debounce(fn, ms = 300) {
    let t;
    return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
  }
  const setDelay = debounce(v => api.post("/api/keyboard/set", { repeat_delay: v }));
  const setRate  = debounce(v => api.post("/api/keyboard/set", { repeat_rate: v }));

  const layoutG = group("Layout");
  layoutG.appendChild(row("Layout", null,
    select(layoutLabels, layoutToLabel[s.layout] || layoutLabels[0], async label => {
      await api.post("/api/keyboard/set", { layout: labelToLayout[label] });
      toast("Layout changed");
    })));
  layoutG.appendChild(row("Variant", null,
    select(variantLabels, variantToLabel[s.variant] ?? "Default", async label => {
      await api.post("/api/keyboard/set", { variant: labelToVariant[label] });
      toast("Variant changed");
    })));
  container.appendChild(layoutG);

  const typingG = group("Typing");
  typingG.appendChild(row("Repeat Delay", "Time before key repeat starts",
    slider(100, 1000, s.repeat_delay, " ms", v => setDelay(Math.round(v)))));
  typingG.appendChild(row("Repeat Rate", "Keys per second when held",
    slider(1, 100, s.repeat_rate, "/s", v => setRate(Math.round(v)))));
  typingG.appendChild(row("Caps Lock → Escape", null,
    toggle(s.caps_escape, async v => {
      await api.post("/api/keyboard/set", { caps_escape: v });
      toast(v ? "Caps Lock now Escape" : "Caps Lock restored");
    })));
  typingG.appendChild(row("Num Lock on startup", null,
    toggle(s.numlock, v => api.post("/api/keyboard/set", { numlock: v }))));
  container.appendChild(typingG);

  const scG = group("Hyprland Shortcuts");
  const data = await api.get("/api/keyboard/shortcuts");
  data.shortcuts.forEach(sc => {
    const keys = el("div", "keys-wrap");
    sc.keys.split(" + ").forEach(k => keys.appendChild(el("span", "keycap", k)));
    scG.appendChild(row(sc.action, null, keys));
  });
  container.appendChild(scG);
}
