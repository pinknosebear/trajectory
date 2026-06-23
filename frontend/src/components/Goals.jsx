import Sparkline from "./Sparkline.jsx";

// Goal trajectory cards. `data` is /api/goals.
export default function Goals({ data, t }) {
  const fmt = (v) => (Number.isInteger(v) ? v.toLocaleString() : v);
  return (
    <section style={{ marginBottom: 32 }}>
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          justifyContent: "space-between",
          marginBottom: 18,
        }}
      >
        <h2
          style={{
            fontFamily: t.display,
            fontWeight: t.headW,
            fontSize: 22,
            margin: 0,
            letterSpacing: -0.2,
          }}
        >
          Where you're heading
        </h2>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
        {data.map((g) => (
          <div
            key={g.label}
            style={{
              background: t.paper,
              border: `1px solid ${t.line}`,
              borderRadius: 12,
              padding: "16px 16px 14px",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: 10,
              }}
            >
              <span style={{ fontSize: 13, color: t.soft, fontWeight: 500 }}>
                {g.label}
              </span>
              <span
                style={{
                  fontSize: 10.5,
                  fontWeight: 600,
                  padding: "2px 7px",
                  borderRadius: 20,
                  color: g.on_track ? t.good : t.accentDeep,
                  background: g.on_track ? "rgba(22,163,74,.1)" : t.accentSoft,
                }}
              >
                {g.on_track ? "on track" : "needs work"}
              </span>
            </div>
            <div style={{ display: "flex", alignItems: "baseline", gap: 5, marginBottom: 10 }}>
              <span style={{ fontFamily: t.display, fontSize: 24, lineHeight: 1 }}>
                {fmt(g.current)}
                {g.unit}
              </span>
              <span style={{ fontSize: 12, color: t.faint }}>
                → {fmt(g.target)}
                {g.unit}
              </span>
            </div>
            <Sparkline
              data={g.trend}
              w={150}
              h={32}
              color={g.on_track ? t.good : t.accent}
              dot
            />
          </div>
        ))}
      </div>
    </section>
  );
}
