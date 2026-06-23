import { useEffect, useMemo, useRef, useState } from "react";
import { api } from "./api.js";
import { buildTokens } from "./tokens.js";
import Sidebar from "./components/Sidebar.jsx";
import Overview from "./components/Overview.jsx";
import Coach from "./components/Coach.jsx";

const t = buildTokens({ accent: "terracotta", surface: "warm", headline: "editorial" });
const todayLabel = new Intl.DateTimeFormat(undefined, {
  weekday: "long",
  month: "long",
  day: "numeric",
}).format(new Date());

export default function App() {
  const [view, setView] = useState("Overview");
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState(null);
  const checkinRef = useRef(null);

  const cssVars = useMemo(
    () => ({
      "--bg": t.bg,
      "--paper": t.paper,
      "--ink": t.ink,
      "--ink-2": t.ink2,
      "--soft": t.soft,
      "--faint": t.faint,
      "--line": t.line,
      "--accent": t.accent,
      "--accent-soft": t.accentSoft,
      "--accent-deep": t.accentDeep,
      "--on-accent": t.onAccent,
      "--good": t.good,
      "--warn": t.warn,
      "--danger": t.danger,
      "--sidebar": t.sidebar,
      "--sidebar-ink": t.sidebarInk,
      "--display": t.display,
      "--body": t.body,
      "--mono": t.mono,
    }),
    []
  );

  useEffect(() => {
    api
      .dashboard("7d")
      .then(setDashboard)
      .catch((e) => setError(e.message));
  }, []);

  function focusCheckin() {
    setView("Overview");
    window.setTimeout(() => {
      checkinRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
    }, 0);
  }

  if (error) {
    return <div className="center-msg">{error} - is the backend running?</div>;
  }

  return (
    <div className="app-shell" style={cssVars}>
      <Sidebar view={view} onViewChange={setView} />
      <main className="content">
        <header className="page-header">
          <div>
            <h1>{view}</h1>
            <p>{todayLabel} · last 7d vs prior 7d</p>
          </div>
          <button className="primary-button" type="button" onClick={focusCheckin}>
            + Check-in
          </button>
        </header>
        {!dashboard ? (
          <div className="panel empty-state">Loading overview…</div>
        ) : view === "Coach" ? (
          <Coach t={t} />
        ) : (
          <Overview
            dashboard={dashboard}
            setDashboard={setDashboard}
            checkinRef={checkinRef}
            t={t}
          />
        )}
      </main>
    </div>
  );
}
