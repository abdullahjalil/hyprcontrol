async function loadPower(container) {
  container.innerHTML = `<h1 class="panel-title">Power</h1>`;

  // Idle and Lock
  const idleG = group("Idle and Lock");
  idleG.appendChild(row("Dim Screen",   "Reduce brightness when idle",
    select(["1 min","2 min","3 min","5 min","Never"], "2 min", () => {})));
  idleG.appendChild(row("Lock Screen",  null,
    select(["3 min","5 min","10 min","30 min","Never"], "5 min", () => {})));
  idleG.appendChild(row("Suspend",      null,
    select(["15 min","30 min","1 hour","Never"], "30 min", () => {})));
  container.appendChild(idleG);

  // Button behaviour
  const btnG = group("Button Behaviour");
  btnG.appendChild(row("Power button", null,
    select(["Suspend","Shutdown","Hibernate","Nothing"], "Suspend", () => {})));
  btnG.appendChild(row("Lid close",    null,
    select(["Suspend","Lock","Nothing"], "Suspend", () => {})));
  container.appendChild(btnG);

  // Quick actions
  const actG = group("Quick Actions");
  const powerGrid = el("div", "power-grid");

  const actions = [
    {
      label: "Lock Screen",
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>`,
      endpoint: "/api/power/lock",
      cls: ""
    },
    {
      label: "Suspend",
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`,
      endpoint: "/api/power/suspend",
      cls: ""
    },
    {
      label: "Reboot",
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>`,
      endpoint: "/api/power/reboot",
      cls: ""
    },
    {
      label: "Shutdown",
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M18.36 6.64a9 9 0 1 1-12.73 0"/><line x1="12" y1="2" x2="12" y2="12"/></svg>`,
      endpoint: "/api/power/shutdown",
      cls: "danger"
    },
  ];

  actions.forEach(a => {
    const b = document.createElement("button");
    b.className = `power-btn ${a.cls}`;
    b.innerHTML = `${a.icon}<span>${a.label}</span>`;
    b.addEventListener("click", () => {
      dialog(
        `${a.label}?`,
        `Are you sure you want to ${a.label.toLowerCase()} the system?`,
        async () => {
          await api.post(a.endpoint);
        },
        a.label
      );
    });
    powerGrid.appendChild(b);
  });

  actG.appendChild(powerGrid);
  container.appendChild(actG);
}
