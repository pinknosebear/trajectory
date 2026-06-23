// AI weekly briefing hero + the experiment CTA. `data` is /api/briefing.
export default function Briefing({ data, t }) {
  return (
    <section style={{ marginBottom: 32 }}>
      <div className="eyebrow" style={{ color: t.accentDeep }}>
        Your weekly briefing · week of {data.week_start}
      </div>
      <h1
        style={{
          fontFamily: t.display,
          fontWeight: 700,
          fontSize: 44,
          lineHeight: 1.12,
          letterSpacing: t.headLS,
          margin: "0 0 20px",
          maxWidth: 760,
          textWrap: "pretty",
        }}
      >
        {data.headline}
      </h1>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          color: t.faint,
          fontSize: 14,
          marginBottom: 40,
        }}
      >
        <span
          style={{
            width: 7,
            height: 7,
            borderRadius: "50%",
            background: t.accent,
            display: "inline-block",
          }}
        />
        Written by your AI coach from 7 days of data
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 24,
          marginBottom: 32,
        }}
      >
        <div>
          <div className="eyebrow" style={{ color: t.accentDeep }}>
            What went well
          </div>
          <p style={{ fontSize: 17, lineHeight: 1.6, color: t.ink2, margin: 0 }}>
            {data.went_well}
          </p>
        </div>
        <div style={{ paddingLeft: 24, borderLeft: `1px solid ${t.line}` }}>
          <div className="eyebrow" style={{ color: t.faint }}>
            What to watch
          </div>
          <p style={{ fontSize: 17, lineHeight: 1.6, color: t.ink2, margin: 0 }}>
            {data.to_watch}
          </p>
        </div>
      </div>

      {/* hero experiment CTA */}
      <div
        className="cta"
        style={{
          background: t.accent,
          color: t.onAccent,
          borderRadius: 16,
          padding: "34px 36px",
        }}
      >
        <div
          className="eyebrow"
          style={{ color: "rgba(255,255,255,.7)", marginBottom: 14 }}
        >
          Your experiment this week
        </div>
        <h2
          style={{
            fontFamily: t.display,
            fontWeight: t.headW,
            fontSize: 28,
            lineHeight: 1.18,
            letterSpacing: -0.3,
            margin: "0 0 24px",
            maxWidth: 620,
            textWrap: "pretty",
          }}
        >
          {data.experiment}
        </h2>
        <div style={{ display: "flex", gap: 14 }}>
          <button
            style={{
              padding: "13px 22px",
              borderRadius: 10,
              border: "none",
              background: "#fff",
              color: t.accentDeep,
              fontFamily: t.body,
              fontSize: 15,
              fontWeight: 600,
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            Start this experiment
          </button>
          <button
            style={{
              padding: "13px 18px",
              borderRadius: 10,
              border: "1px solid rgba(255,255,255,.4)",
              background: "transparent",
              color: "#fff",
              fontFamily: t.body,
              fontSize: 15,
              fontWeight: 500,
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            Suggest another
          </button>
        </div>
      </div>
    </section>
  );
}
