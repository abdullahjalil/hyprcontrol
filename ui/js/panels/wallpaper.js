async function loadWallpaper(container) {
  container.innerHTML = `<h1 class="panel-title">Wallpaper</h1>`;
  const data = await api.get("/api/wallpaper/list");

  // Current preview
  const previewGroup = group("Current Wallpaper");
  if (data.current) {
    const img = el("img", "wp-current");
    img.src = `/api/wallpaper/serve?path=${encodeURIComponent(data.current)}`;
    img.onerror = () => img.style.display = "none";
    const wrap = el("div", "");
    wrap.style.cssText = "padding:12px 18px 4px";
    wrap.appendChild(img);
    previewGroup.appendChild(wrap);
  }
  const pathRow = row("Path", data.current || "Not set", null);
  previewGroup.appendChild(pathRow);
  container.appendChild(previewGroup);

  // Options
  const optsGroup = group("Options");
  optsGroup.appendChild(row("Fill Mode", null,
    select(["fill","fit","center","tile"], "fill", () => {})));
  container.appendChild(optsGroup);

  // Grid
  const gridGroup = group("Available Wallpapers");
  const grid = el("div", "wp-grid");
  data.images.forEach(path => {
    const thumb = el("div", `wp-thumb${path === data.current ? " selected" : ""}`);
    const img = el("img");
    img.src = `/api/wallpaper/serve?path=${encodeURIComponent(path)}`;
    img.loading = "lazy";
    img.onerror = () => thumb.style.display = "none";
    thumb.appendChild(img);
    thumb.addEventListener("click", async () => {
      grid.querySelectorAll(".wp-thumb").forEach(t => t.classList.remove("selected"));
      thumb.classList.add("selected");
      pathRow.querySelector(".row-sub").textContent = path;
      await api.post("/api/wallpaper/set", { path });
      toast("Wallpaper set");
    });
    grid.appendChild(thumb);
  });
  gridGroup.appendChild(grid);
  container.appendChild(gridGroup);
}
