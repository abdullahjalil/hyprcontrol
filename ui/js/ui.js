// ui.js — shared UI building blocks

function el(tag, cls, html = "") {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html) e.innerHTML = html;
  return e;
}

function group(title, headerAction = null) {
  const g = el("div", "group");
  if (title || headerAction) {
    const h = el("div", "group-header");
    if (title) h.appendChild(el("div", "group-title", title));
    if (headerAction) h.appendChild(headerAction);
    g.appendChild(h);
  }
  return g;
}

function row(label, sub, right) {
  const r = el("div", "row");
  const l = el("div", "row-left");
  l.appendChild(el("div", "row-label", label));
  if (sub) l.appendChild(el("div", "row-sub", sub));
  r.appendChild(l);
  const rr = el("div", "row-right");
  if (right) {
    if (Array.isArray(right)) right.forEach(w => rr.appendChild(w));
    else rr.appendChild(right);
  }
  r.appendChild(rr);
  return r;
}

function toggle(checked, onChange) {
  const label = el("label", "toggle");
  const input = el("input");
  input.type = "checkbox";
  input.checked = checked;
  input.addEventListener("change", () => onChange(input.checked));
  const track = el("div", "toggle-track");
  const thumb = el("div", "toggle-thumb");
  label.appendChild(input);
  label.appendChild(track);
  label.appendChild(thumb);
  return label;
}

function slider(min, max, value, unit, onChange) {
  const wrap = el("div", "slider-wrap");
  const input = el("input");
  input.type = "range";
  input.min = min; input.max = max; input.value = value;
  const val = el("span", "slider-val", value + unit);

  function updateTrack() {
    const pct = ((input.value - min) / (max - min)) * 100;
    input.style.setProperty("--pct", pct + "%");
    val.textContent = Math.round(input.value) + unit;
  }

  input.addEventListener("input", () => { updateTrack(); onChange(+input.value); });
  updateTrack();
  wrap.appendChild(input);
  wrap.appendChild(val);
  return wrap;
}

function select(options, current, onChange) {
  const s = el("select");
  options.forEach(o => {
    const opt = el("option");
    opt.value = o; opt.textContent = o;
    if (o === current) opt.selected = true;
    s.appendChild(opt);
  });
  s.addEventListener("change", () => onChange(s.value));
  return s;
}

function btn(label, cls, onClick) {
  const b = el("button", `btn ${cls}`, label);
  b.addEventListener("click", onClick);
  return b;
}

function badge(text, type = "accent") {
  return el("span", `badge badge-${type}`, text);
}

function spinner() {
  return el("div", "spinner");
}

let toastTimer;
function toast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove("show"), 2500);
}

function dialog(title, body, onConfirm, confirmLabel = "OK", inputPlaceholder = null) {
  const overlay = el("div", "dialog-overlay");
  const d = el("div", "dialog");
  d.appendChild(el("div", "dialog-title", title));
  d.appendChild(el("div", "dialog-body", body));

  let input;
  if (inputPlaceholder) {
    input = el("input");
    input.type = "password";
    input.placeholder = inputPlaceholder;
    d.appendChild(input);
  }

  const btns = el("div", "dialog-btns");
  btns.appendChild(btn("Cancel", "btn-default", () => overlay.remove()));
  btns.appendChild(btn(confirmLabel, "btn-accent", () => {
    overlay.remove();
    onConfirm(input ? input.value : null);
  }));
  d.appendChild(btns);
  overlay.appendChild(d);
  document.body.appendChild(overlay);
  if (input) setTimeout(() => input.focus(), 50);
}
