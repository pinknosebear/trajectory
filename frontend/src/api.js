// Tiny fetch wrapper around the FastAPI backend (proxied via vite.config.js).
async function get(path) {
  const res = await fetch(`/api${path}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const api = {
  briefing: () => get("/briefing"),
  goals: () => get("/goals"),
  mealResponse: (name) => get(`/meals/response?name=${encodeURIComponent(name)}`),
  labs: (marker = "eGFR") => get(`/labs?marker=${encodeURIComponent(marker)}`),
};
