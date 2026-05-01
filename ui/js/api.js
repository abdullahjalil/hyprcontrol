// api.js — fetch wrapper for all backend calls
const api = {
  async get(endpoint) {
    const r = await fetch(endpoint);
    return r.json();
  },
  async post(endpoint, data = {}) {
    const r = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return r.json();
  }
};
