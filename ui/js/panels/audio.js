async function loadAudio(container) {
  container.innerHTML = `<h1 class="panel-title">Audio</h1>`;
  const data = await api.get("/api/audio/status");

  const outGroup = group("Output");
  outGroup.appendChild(row("Output Device", null,
    select(data.sinks, data.default_sink, async v => {
      await api.post("/api/audio/sink", { name: v }); toast("Output device changed");
    })));
  outGroup.appendChild(row("Volume", null,
    slider(0, 150, data.volume, "%", async v => {
      await api.post("/api/audio/volume", { value: v });
    })));
  outGroup.appendChild(row("Mute", null,
    toggle(data.muted, async v => {
      await api.post("/api/audio/mute", { muted: v });
    })));
  container.appendChild(outGroup);

  const inGroup = group("Input");
  inGroup.appendChild(row("Input Device", null,
    select(data.sources, data.default_source, async v => {
      await api.post("/api/audio/source", { name: v }); toast("Input device changed");
    })));
  inGroup.appendChild(row("Microphone Volume", null,
    slider(0, 100, data.mic_volume, "%", async v => {
      await api.post("/api/audio/mic_volume", { value: v });
    })));
  inGroup.appendChild(row("Mute Microphone", null,
    toggle(data.mic_muted, async v => {
      await api.post("/api/audio/mic_mute", { muted: v });
    })));
  container.appendChild(inGroup);
}
