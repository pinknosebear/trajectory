const windows = ["14d", "30d", "90d"];

export default function GlucoseChart({ series, window, onWindowChange, loading }) {
  const points = series?.points || [];
  const width = 680;
  const height = 260;
  const pad = 34;
  const all = points.flatMap((p) => [p.low, p.high, p.mean]).filter((v) => v != null);

  let body = <div className="empty-state">No glucose readings in this window.</div>;
  if (points.length && all.length) {
    const min = Math.min(60, ...all);
    const max = Math.max(210, ...all);
    const span = max - min || 1;
    const x = (i) => pad + (i / Math.max(points.length - 1, 1)) * (width - pad * 2);
    const y = (v) => pad + (1 - (v - min) / span) * (height - pad * 2);
    const meanPath = points
      .map((p, i) => `${i === 0 ? "M" : "L"}${x(i).toFixed(1)},${y(p.mean).toFixed(1)}`)
      .join(" ");
    const loY = y(series.band.lo);
    const hiY = y(series.band.hi);

    body = (
      <svg className="glucose-svg" viewBox={`0 0 ${width} ${height}`} role="img">
        <rect x={pad} y={hiY} width={width - pad * 2} height={loY - hiY} className="target-band" />
        {[70, 140, 180].map((tick) => (
          <g key={tick}>
            <line x1={pad} x2={width - pad} y1={y(tick)} y2={y(tick)} className="grid-line" />
            <text x={6} y={y(tick) + 4}>{tick}</text>
          </g>
        ))}
        {points.map((p, i) => (
          <line
            key={p.date}
            x1={x(i)}
            x2={x(i)}
            y1={y(p.low)}
            y2={y(p.high)}
            className="range-line"
          />
        ))}
        <path d={meanPath} className="mean-line" />
        {points.map((p, i) => (
          <circle key={`${p.date}-mean`} cx={x(i)} cy={y(p.mean)} r="2.8" className="mean-dot" />
        ))}
      </svg>
    );
  }

  return (
    <section className="panel chart-panel">
      <div className="panel-head">
        <div>
          <h2>Glucose</h2>
          <p>Daily mean with observed low-high range</p>
        </div>
        <div className="segmented">
          {windows.map((w) => (
            <button
              key={w}
              type="button"
              className={window === w ? "active" : ""}
              onClick={() => onWindowChange(w)}
            >
              {w}
            </button>
          ))}
        </div>
      </div>
      {loading ? <div className="empty-state">Loading glucose…</div> : body}
    </section>
  );
}
