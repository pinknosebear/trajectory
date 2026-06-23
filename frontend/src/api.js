async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `${res.status} ${res.statusText}`);
  }
  return res.json();
}

const get = (path) => request(path);
const post = (path, payload) =>
  request(path, { method: "POST", body: JSON.stringify(payload) });

export const api = {
  dashboard: (window = "7d") => get(`/v1/dashboard?window=${encodeURIComponent(window)}`),
  kpis: (window = "7d") => get(`/v1/kpis?window=${encodeURIComponent(window)}`),
  glucoseSeries: (window = "14d") =>
    get(`/v1/glucose/series?window=${encodeURIComponent(window)}`),
  correlations: (window = "30d") =>
    get(`/v1/correlations?window=${encodeURIComponent(window)}`),
  checkinToday: () => get("/v1/checkin/today"),
  submitCheckin: (payload) => post("/v1/checkin", payload),
  briefing: () => get("/briefing"),
  goals: () => get("/goals"),
  mealResponse: (name) => get(`/meals/response?name=${encodeURIComponent(name)}`),
  labs: (marker = "eGFR") => get(`/labs?marker=${encodeURIComponent(marker)}`),
};
