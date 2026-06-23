import { useEffect, useState } from "react";
import { api } from "./api.js";
import { buildTokens } from "./tokens.js";
import Briefing from "./components/Briefing.jsx";
import MealResponse from "./components/MealResponse.jsx";
import Goals from "./components/Goals.jsx";

// Swap these to re-skin (mirrors the Tweaks panel from the mockups).
const t = buildTokens({ accent: "terracotta", surface: "warm", headline: "editorial" });

export default function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      api.briefing(),
      api.goals(),
      api.mealResponse("Rice & dal"),
    ])
      .then(([briefing, goals, meal]) => setData({ briefing, goals, meal }))
      .catch((e) => setError(e.message));
  }, []);

  if (error)
    return (
      <div className="center-msg">
        {error} — is the backend running? (uvicorn main:app --reload)
      </div>
    );
  if (!data) return <div className="center-msg">Loading…</div>;

  return (
    <div style={{ background: t.bg, color: t.ink, minHeight: "100vh" }}>
      {/* top bar */}
      <header
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "20px 48px",
          borderBottom: `1px solid ${t.line}`,
          background: t.paper,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
          <BrandMark t={t} />
          <span style={{ fontSize: 18, fontWeight: 600, letterSpacing: -0.2 }}>
            Trajectory
          </span>
        </div>
        <nav
          style={{
            display: "flex",
            alignItems: "center",
            gap: 26,
            fontSize: 14,
            color: t.soft,
          }}
        >
          <span>Overview</span>
          <span>Goals</span>
          <span>Glucose</span>
          <span>Experiments</span>
          <span
            style={{
              width: 30,
              height: 30,
              borderRadius: "50%",
              background: t.accentSoft,
              color: t.accentDeep,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: 600,
              fontSize: 13,
            }}
          >
            R
          </span>
        </nav>
      </header>

      <main className="wrap">
        <Briefing data={data.briefing} t={t} />
        <MealResponse data={data.meal} t={t} />
        <Goals data={data.goals} t={t} />
      </main>
    </div>
  );
}

function BrandMark({ t, size = 24 }) {
  return (
    <span
      style={{
        width: size,
        height: size,
        borderRadius: size * 0.27,
        background: t.accent,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexShrink: 0,
      }}
    >
      <svg
        width={size * 0.62}
        height={size * 0.62}
        viewBox="0 0 16 16"
        fill="none"
        stroke={t.onAccent}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M2 11 L6 7 L9 9.5 L14 4" />
        <path d="M10.5 4 L14 4 L14 7.5" />
      </svg>
    </span>
  );
}
