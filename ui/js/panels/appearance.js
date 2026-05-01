async function loadAppearance(container) {
  container.innerHTML = `<h1 class="panel-title">Appearance</h1>`;
  const data = await api.get("/api/appearance/status");

  const themeGroup = group("GTK Theme");
  themeGroup.appendChild(row("Theme", null,
    select(data.themes, data.gtk_theme, async v => {
      await api.post("/api/appearance/set", { gtk_theme: v }); toast("Theme applied");
    })));
  themeGroup.appendChild(row("Icon Theme", null,
    select(data.icons, data.icon_theme, async v => {
      await api.post("/api/appearance/set", { icon_theme: v }); toast("Icon theme applied");
    })));
  themeGroup.appendChild(row("Cursor Theme", null,
    select(data.cursors, data.cursor_theme, async v => {
      await api.post("/api/appearance/set", { cursor_theme: v }); toast("Cursor theme applied");
    })));
  themeGroup.appendChild(row("Cursor Size", null,
    slider(16, 64, data.cursor_size, "px", async v => {
      await api.post("/api/appearance/set", { cursor_size: v });
    })));
  container.appendChild(themeGroup);

  const accentGroup = group("Accent Colors");
  const swatches = [
    { color: "#d4914a", name: "Desert Amber" },
    { color: "#c95f2e", name: "Terracotta"   },
    { color: "#c4a0b8", name: "Mauve"         },
    { color: "#7a8fa0", name: "Sky"           },
    { color: "#8a9a6a", name: "Sage"          },
    { color: "#b89a80", name: "Sand"          },
  ];
  const swatchRow = el("div", "swatch-row");
  swatches.forEach(s => {
    const sw = el("div", "swatch");
    sw.style.background = s.color;
    sw.title = s.name;
    sw.addEventListener("click", () => {
      swatchRow.querySelectorAll(".swatch").forEach(x => x.classList.remove("selected"));
      sw.classList.add("selected");
      toast(`Accent: ${s.name}`);
    });
    swatchRow.appendChild(sw);
  });
  swatchRow.firstChild.classList.add("selected");
  const swWrap = el("div", "");
  swWrap.style.cssText = "padding:10px 18px 14px";
  swWrap.appendChild(swatchRow);
  accentGroup.appendChild(swWrap);
  container.appendChild(accentGroup);

  const fontGroup = group("Font");
  fontGroup.appendChild(row("Monospace Font", null,
    select(["JetBrains Mono","Fira Code","Hack","Noto Mono"],
      "JetBrains Mono", () => {})));
  fontGroup.appendChild(row("Font Size", null,
    select(["9","10","11","12","13","14"], "11", () => {})));
  container.appendChild(fontGroup);
}
