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

  // Track current speed/bezier so changing one preserves the other.
  let animSpeed  = data.anim ? data.anim.speed  : 5;
  let animBezier = data.anim ? data.anim.bezier : "overshot";
  const curves   = (data.anim && data.anim.curves) || ["overshot", "linear", "easeInOut", "bounce", "easeOutQuint"];

  let animTimer;
  function applyAnim() {
    clearTimeout(animTimer);
    animTimer = setTimeout(() => {
      api.post("/api/hyprland/animation", { speed: animSpeed, bezier: animBezier });
    }, 300);
  }

  animG.appendChild(row("Speed", "Higher is faster", slider(1, 10, animSpeed, "", v => {
    animSpeed = Math.round(v); applyAnim();
  })));
  animG.appendChild(row("Bezier Curve", null,
    select(curves, animBezier, v => { animBezier = v; applyAnim(); toast("Curve: " + v); })));
  container.appendChild(animG);

  const inputG = group("Input Behaviour");
  inputG.appendChild(kwToggle("Focus Follows Mouse", "focus_mouse", data.focus_mouse));
  inputG.appendChild(kwToggle("Natural Scroll (Touchpad)", "natural_scroll", data.natural_scroll));
  inputG.appendChild(kwToggle("Disable Touchpad While Typing", "disable_while_typing", data.disable_while_typing));
  inputG.appendChild(row("Tiling Layout", null,
    select(["dwindle", "master"], data.layout, async v => {
      await api.post("/api/hyprland/set", { layout: v }); toast("Layout changed");
    })));
  container.appendChild(inputG);

  const cfgG = group("Configuration");
  const fmtLabel = data.config_format === "lua" ? "Lua" : "hyprlang";
  cfgG.appendChild(row("Config File", `${data.config_path}  ·  ${fmtLabel}`,
    [
      btn("Edit", "btn-ghost btn-sm", () => toast("Open in terminal: nvim " + data.config_path)),
      btn("Reload", "btn-accent btn-sm", async () => {
        await api.post("/api/hyprland/reload");
        toast("✓ Hyprland config reloaded");
      }),
    ]
  ));
  cfgG.appendChild(row("Save current settings",
    "Writes a managed block to your active config so tweaks survive a restart",
    btn("Save to config", "btn-accent btn-sm", async () => {
      // Persist the current live values (re-read so slider/toggle changes count).
      const cur = await api.get("/api/hyprland/status");
      const res = await api.post("/api/hyprland/save", {
        border_size:   cur.border_size,
        corner_radius: cur.corner_radius,
        gaps_out:      cur.gaps_out,
        blur:          cur.blur,
        animations:    cur.animations,
        focus_mouse:   cur.focus_mouse,
        layout:        cur.layout,
        natural_scroll:       cur.natural_scroll,
        disable_while_typing: cur.disable_while_typing,
      });
      toast(res.ok ? `✓ Saved to ${fmtLabel} config` : "✗ Save failed");
    })
  ));
  container.appendChild(cfgG);
}
