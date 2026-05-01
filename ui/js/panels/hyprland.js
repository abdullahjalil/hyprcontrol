async function loadHyprland(container) {
  container.innerHTML = `<h1 class="panel-title">Hyprland</h1>`;
  const data = await api.get("/api/hyprland/status");

  function kwSlider(label, key, min, max, val, unit) {
    return row(label, null, slider(min, max, val, unit, async v => {
      await api.post("/api/hyprland/set", { [key]: Math.round(v) });
    }));
  }

  function kwToggle(label, key, val) {
    return row(label, null, toggle(val, async v => {
      await api.post("/api/hyprland/set", { [key]: v });
    }));
  }

  const winG = group("Window Decoration");
  winG.appendChild(kwSlider("Border Width",   "border_size",   0, 8,  data.border_size,   " px"));
  winG.appendChild(kwSlider("Corner Radius",  "corner_radius", 0, 20, data.corner_radius, " px"));
  winG.appendChild(kwSlider("Gap Size",       "gaps_out",      0, 30, data.gaps_out,      " px"));
  winG.appendChild(kwToggle("Blur Windows",   "blur",          data.blur));
  container.appendChild(winG);

  const animG = group("Animations");
  animG.appendChild(kwToggle("Enable Animations", "animations", data.animations));
  animG.appendChild(row("Speed", null, slider(1, 10, 5, "", () => {})));
  animG.appendChild(row("Bezier Curve", null,
    select(["overshot","linear","easeInOut","bounce","easeOutQuint"], "overshot", () => {})));
  container.appendChild(animG);

  const inputG = group("Input Behaviour");
  inputG.appendChild(kwToggle("Focus Follows Mouse",       "focus_mouse", data.focus_mouse));
  inputG.appendChild(row("Scroll to Change Workspace", null, toggle(true, () => {})));
  inputG.appendChild(row("Touchpad Gestures",          null, toggle(true, () => {})));
  inputG.appendChild(row("Tiling Layout", null,
    select(["dwindle","master"], data.layout, async v => {
      await api.post("/api/hyprland/set", { layout: v }); toast("Layout changed");
    })));
  container.appendChild(inputG);

  const cfgG = group("Configuration");
  cfgG.appendChild(row("Config File", data.config_path,
    [
      btn("Edit", "btn-ghost btn-sm", () => toast("Open in terminal: nvim " + data.config_path)),
      btn("Reload", "btn-accent btn-sm", async () => {
        await api.post("/api/hyprland/reload");
        toast("✓ Hyprland config reloaded");
      }),
    ]
  ));
  container.appendChild(cfgG);
}
