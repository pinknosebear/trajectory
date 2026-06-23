import { useEffect, useState } from "react";
import { api } from "../api.js";
import Briefing from "./Briefing.jsx";
import MealResponse from "./MealResponse.jsx";
import Goals from "./Goals.jsx";

export default function Coach({ t }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([api.briefing(), api.goals(), api.mealResponse("Rice & dal")])
      .then(([briefing, goals, meal]) => setData({ briefing, goals, meal }))
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="panel error-state">{error}</div>;
  if (!data) return <div className="panel empty-state">Loading coach…</div>;

  return (
    <div className="coach-view">
      <Briefing data={data.briefing} t={t} />
      <MealResponse data={data.meal} t={t} />
      <Goals data={data.goals} t={t} />
    </div>
  );
}
