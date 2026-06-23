import Sparkline from "./primitives/Sparkline.jsx";

export default function KpiCard({ kpi }) {
  const delta = kpi.delta_pct;
  return (
    <article className="kpi-card">
      <div className="kpi-top">
        <span>{kpi.label}</span>
        <span className={kpi.good ? "pill good" : "pill caution"}>
          {delta == null ? "new" : `${delta > 0 ? "+" : ""}${delta}%`}
        </span>
      </div>
      <div className="kpi-value">
        {kpi.value ?? "—"}
        <small>{kpi.unit}</small>
      </div>
      {kpi.spark?.length ? (
        <Sparkline data={kpi.spark} w={210} h={44} color="var(--accent)" dot />
      ) : (
        <div className="empty-mini">No recent data</div>
      )}
    </article>
  );
}
