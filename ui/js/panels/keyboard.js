async function loadKeyboard(container) {
  container.innerHTML = `<h1 class="panel-title">Keyboard</h1>`;

  const layoutG = group("Layout");
  layoutG.appendChild(row("Layout",  null, select(["English (UK)","English (US)","Spanish","French","German"],"English (UK)",()=>{})));
  layoutG.appendChild(row("Variant", null, select(["Default","Colemak","Dvorak","Workman"],"Default",()=>{})));
  container.appendChild(layoutG);

  const typingG = group("Typing");
  typingG.appendChild(row("Repeat Delay", "Time before key repeat starts",
    slider(100, 1000, 300, " ms", () => {})));
  typingG.appendChild(row("Repeat Rate", "Keys per second when held",
    slider(1, 100, 50, "/s", () => {})));
  typingG.appendChild(row("Caps Lock → Escape", null, toggle(true, () => {})));
  typingG.appendChild(row("Num Lock on startup", null, toggle(true, () => {})));
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
