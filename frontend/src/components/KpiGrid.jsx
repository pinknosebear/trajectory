import KpiCard from "./KpiCard.jsx";

export default function KpiGrid({ kpis = [] }) {
  return (
    <section className="kpi-grid">
      {kpis.map((kpi) => (
        <KpiCard kpi={kpi} key={kpi.key} />
      ))}
    </section>
  );
}
