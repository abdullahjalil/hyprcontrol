async function loadAppearance(container) {
  container.innerHTML = `<h1 class="panel-title">Appearance</h1>`;
  const data = await api.get("/api/appearance/status");

  // Track pending changes
  const pending = {
    gtk_theme:    data.gtk_theme,
    icon_theme:   data.icon_theme,
    cursor_theme: data.cursor_theme,
    cursor_size:  data.cursor_size,
    font:         data.font,
  };

  // ── Theme group ─────────────────────────────────────────────
  const themeG = group("GTK Theme");

  themeG.appendChild(row("Theme", "Applies to all GTK apps",
    select(data.themes, data.gtk_theme, v => { pending.gtk_theme = v; markDirty(); })));

  themeG.appendChild(row("Icon Theme", "Folder and app icons",
    select(data.icons, data.icon_theme, v => { pending.icon_theme = v; markDirty(); })));

  container.appendChild(themeG);

  // ── Cursor group ─────────────────────────────────────────────
  const cursorG = group("Cursor");

  cursorG.appendChild(row("Cursor Theme", "Takes effect on new windows",
    select(data.cursors, data.cursor_theme, v => { pending.cursor_theme = v; markDirty(); })));

  cursorG.appendChild(row("Cursor Size", null,
    slider(16, 64, data.cursor_size, "px", v => { pending.cursor_size = v; markDirty(); })));

  container.appendChild(cursorG);

  // ── Font group ───────────────────────────────────────────────
  const fontG = group("Font");

  fontG.appendChild(row("Monospace Font", "Terminal and code editors",
    select(
      ["JetBrains Mono", "Fira Code", "Hack", "Noto Mono", "Source Code Pro"],
      "JetBrains Mono",
      v => { markDirty(); }
    )));

  fontG.appendChild(row("Font Size", null,
    select(["9","10","11","12","13","14"], "11", () => { markDirty(); })));

  container.appendChild(fontG);

  // ── Accent swatches ──────────────────────────────────────────
  const accentG = group("Accent Color");
  const swatches = [
    { color: "#d4914a", name: "Desert Amber" },
    { color: "#c95f2e", name: "Terracotta"   },
    { color: "#c4a0b8", name: "Mauve"        },
    { color: "#7a8fa0", name: "Sky"          },
    { color: "#8a9a6a", name: "Sage"         },
    { color: "#b89a80", name: "Sand"         },
  ];
  const swatchWrap = el("div", "");
  swatchWrap.style.cssText = "padding: 10px 18px 14px";
  const swatchRow = el("div", "swatch-row");
  swatches.forEach(s => {
    const sw = el("div", "swatch");
    sw.style.background = s.color;
    sw.title = s.name;
    sw.addEventListener("click", () => {
      swatchRow.querySelectorAll(".swatch").forEach(x => x.classList.remove("selected"));
      sw.classList.add("selected");
      markDirty();
    });
    swatchRow.appendChild(sw);
  });
  swatchRow.firstChild.classList.add("selected");
  swatchWrap.appendChild(swatchRow);
  accentG.appendChild(swatchWrap);
  container.appendChild(accentG);

  // ── Apply bar ────────────────────────────────────────────────
  const applyBar = el("div", "");
  applyBar.style.cssText = `
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #2e1820;
    border-radius: 10px;
    padding: 12px 18px;
    margin-bottom: 16px;
    opacity: 0;
    transition: opacity 0.2s;
    pointer-events: none;
  `;

  const applyMsg = el("span", "row-sub", "You have unsaved appearance changes");
  const applyBtns = el("div", "");
  applyBtns.style.cssText = "display:flex;gap:8px";

  const resetBtn = btn("Reset", "btn-default btn-sm", async () => {
    // Reload page to reset all dropdowns
    loadAppearance(container);
  });

  const applyBtn = btn("⬡ Apply", "btn-accent btn-sm", async () => {
    applyBtn.textContent = "Applying…";
    applyBtn.disabled = true;
    try {
      await api.post("/api/appearance/apply", pending);
      toast("✓ Appearance applied — new windows will use the updated settings");
      markClean();
    } catch (e) {
      toast("Error applying settings");
    } finally {
      applyBtn.textContent = "⬡ Apply";
      applyBtn.disabled = false;
    }
  });

  applyBtns.appendChild(resetBtn);
  applyBtns.appendChild(applyBtn);
  applyBar.appendChild(applyMsg);
  applyBar.appendChild(applyBtns);

  // Insert apply bar at top of content (after title)
  const title = container.querySelector(".panel-title");
  title.insertAdjacentElement("afterend", applyBar);

  function markDirty() {
    applyBar.style.opacity = "1";
    applyBar.style.pointerEvents = "auto";
  }

  function markClean() {
    applyBar.style.opacity = "0";
    applyBar.style.pointerEvents = "none";
  }
}
