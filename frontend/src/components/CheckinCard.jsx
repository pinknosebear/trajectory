import { forwardRef, useState } from "react";
import Dots from "./primitives/Dots.jsx";

function CheckinCard({ checkin, onSubmit }, ref) {
  const [form, setForm] = useState({ mood: 3, energy: 3, stress: 3, note: "" });
  const [saving, setSaving] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setSaving(true);
    try {
      await onSubmit({ ...form, note: form.note.trim() || null });
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="panel checkin-card" ref={ref}>
      <div className="panel-head compact">
        <h2>Today's Check-in</h2>
      </div>
      {checkin ? (
        <div className="logged-state">
          <div className="logged-grid">
            <span>Mood <b>{checkin.mood}/5</b></span>
            <span>Energy <b>{checkin.energy}/5</b></span>
            <span>Stress <b>{checkin.stress}/5</b></span>
          </div>
          {checkin.note && <p>{checkin.note}</p>}
        </div>
      ) : (
        <form onSubmit={submit} className="checkin-form">
          {["mood", "energy", "stress"].map((key) => (
            <label key={key}>
              <span>{key}</span>
              <Dots
                label={key}
                value={form[key]}
                onChange={(value) => setForm((current) => ({ ...current, [key]: value }))}
              />
            </label>
          ))}
          <textarea
            value={form.note}
            maxLength={280}
            placeholder="Optional note"
            onChange={(e) => setForm((current) => ({ ...current, note: e.target.value }))}
          />
          <button className="primary-button" type="submit" disabled={saving}>
            {saving ? "Saving…" : "Log check-in"}
          </button>
        </form>
      )}
    </section>
  );
}

export default forwardRef(CheckinCard);
