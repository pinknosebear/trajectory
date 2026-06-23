import Ring from "./primitives/Ring.jsx";

export default function GoalRingBand({ overview }) {
  const delta = overview?.delta;
  return (
    <section className="goal-band">
      <div className="score-block">
        <div className="score">{overview?.score ?? "—"}%</div>
        <div className={delta >= 0 ? "score-delta good" : "score-delta"}>
          {delta == null ? "No prior score" : `${delta >= 0 ? "+" : ""}${delta} vs prior`}
        </div>
      </div>
      <div className="rings">
        {(overview?.rings || []).map((ring) => (
          <div className="ring-item" key={ring.key}>
            <Ring value={ring.pct} color={ring.on_track ? "var(--good)" : "var(--accent)"} />
            <div>
              <strong>{ring.label}</strong>
              <span>
                {ring.current}
                {ring.unit} / {ring.target}
                {ring.unit}
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
