export default function CorrelationList({ items = [] }) {
  return (
    <section className="panel">
      <div className="panel-head compact">
        <h2>Correlations</h2>
      </div>
      {items.length ? (
        <div className="correlation-list">
          {items.map((item) => (
            <article key={item.label}>
              <div>
                <strong>{item.label}</strong>
                <span>{item.note}</span>
              </div>
              <b>{item.r.toFixed(2)}</b>
            </article>
          ))}
        </div>
      ) : (
        <div className="empty-state">Not enough paired daily data yet.</div>
      )}
    </section>
  );
}
