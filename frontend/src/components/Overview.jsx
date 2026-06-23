import { useEffect, useState } from "react";
import { api } from "../api.js";
import GoalRingBand from "./GoalRingBand.jsx";
import KpiGrid from "./KpiGrid.jsx";
import GlucoseChart from "./GlucoseChart.jsx";
import CorrelationList from "./CorrelationList.jsx";
import CheckinCard from "./CheckinCard.jsx";
import MealResponse from "./MealResponse.jsx";

export default function Overview({ dashboard, setDashboard, checkinRef, t }) {
  const [chartWindow, setChartWindow] = useState("14d");
  const [series, setSeries] = useState(dashboard.glucose_series);
  const [loadingSeries, setLoadingSeries] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoadingSeries(true);
    api
      .glucoseSeries(chartWindow)
      .then((next) => {
        if (!cancelled) setSeries(next);
      })
      .catch(() => {
        if (!cancelled) setSeries({ window: chartWindow, band: { lo: 70, hi: 180 }, points: [] });
      })
      .finally(() => {
        if (!cancelled) setLoadingSeries(false);
      });
    return () => {
      cancelled = true;
    };
  }, [chartWindow]);

  async function submitCheckin(payload) {
    await api.submitCheckin(payload);
    const today = await api.checkinToday();
    setDashboard((current) => ({ ...current, checkin_today: today }));
  }

  return (
    <>
      <GoalRingBand overview={dashboard.overview} />
      <KpiGrid kpis={dashboard.kpis} />
      <div className="lower-grid">
        <div className="main-column">
          <GlucoseChart
            series={series}
            window={chartWindow}
            onWindowChange={setChartWindow}
            loading={loadingSeries}
          />
          <MealResponse data={dashboard.meal_response} t={t} />
        </div>
        <div className="side-column">
          <CorrelationList items={dashboard.correlations} />
          <CheckinCard
            ref={checkinRef}
            checkin={dashboard.checkin_today}
            onSubmit={submitCheckin}
          />
        </div>
      </div>
    </>
  );
}
