import Sparkline from "./Sparkline.jsx";

// "What you ate, measured" — compares logged instances of the same meal and
// the glucose response each produced. `data` is /api/meals/response.
export default function MealResponse({ data, t }) {
  const instances = data.instances || [];
  // Find a no-walk and a walk instance to contrast (falls back to first two).
  const noWalk = instances.find((i) => !i.walked_after) || instances[0];
  const walk = instances.find((i) => i.walked_after) || instances[1] || instances[0];

  const curveVals = (inst) => (inst?.curve || []).map((p) => p.mgdl);
  const delta =
    noWalk && walk && noWalk.peak_mgdl != null && walk.peak_mgdl != null
      ? noWalk.peak_mgdl - walk.peak_mgdl
      : null;

  return (
    <section
      style={{
        marginBottom: 32,
        background: t.paper,
        border: `1px solid ${t.line}`,
        borderRadius: 16,
        padding: "28px 30px",
      }}
    >
      <div className="eyebrow" style={{ color: t.accentDeep }}>
        What you ate, measured
      </div>
      <h2
        style={{
          fontFamily: t.display,
          fontWeight: t.headW,
          fontSize: 24,
          letterSpacing: -0.2,
          margin: "0 0 6px",
        }}
      >
        {data.meal}: same plate, two readings
      </h2>
      <p style={{ fontSize: 15, color: t.soft, margin: "0 0 24px", lineHeight: 1.55 }}>
        The only difference between these two dinners was a short walk afterward.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        {/* No walk */}
        <Instance
          t={t}
          label="No walk after"
          inst={noWalk}
          peakColor={t.warn}
          curve={curveVals(noWalk)}
          curve2={curveVals(walk)}
        />
        {/* Walk + takeaway */}
        <div>
          <PeakHeader t={t} label="12-min walk after" inst={walk} peakColor={t.good} />
          <div
            style={{
              background: t.accentSoft,
              borderRadius: 10,
              padding: "16px 18px",
              fontSize: 15,
              lineHeight: 1.55,
              color: t.ink,
            }}
          >
            Movement pulls glucose into muscle cells right after a meal — the walk
            did the work your medication usually has to do alone.
            {delta != null && (
              <>
                {" "}
                <strong>{delta} mg/dL lower peak</strong> for the same food.
              </>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

function PeakHeader({ t, label, inst, peakColor }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 14 }}>
      <div
        style={{
          width: 72,
          height: 72,
          borderRadius: 8,
          flexShrink: 0,
          background: t.bg,
          border: `1px solid ${t.line}`,
          backgroundImage:
            "repeating-linear-gradient(45deg, rgba(0,0,0,.04) 0 6px, transparent 6px 12px)",
        }}
      />
      <div>
        <div style={{ fontSize: 13.5, fontWeight: 600 }}>{label}</div>
        <div
          style={{
            fontFamily: t.mono,
            fontSize: 22,
            fontWeight: 500,
            letterSpacing: -0.5,
            color: peakColor,
            marginTop: 4,
          }}
        >
          {inst?.peak_mgdl ?? "—"} mg/dL peak
        </div>
        {inst?.delta != null && (
          <div style={{ fontSize: 12.5, color: t.faint, marginTop: 2 }}>
            +{inst.delta} above baseline
          </div>
        )}
      </div>
    </div>
  );
}

function Instance({ t, label, inst, peakColor, curve, curve2 }) {
  return (
    <div>
      <PeakHeader t={t} label={label} inst={inst} peakColor={peakColor} />
      <Sparkline
        data={curve}
        data2={curve2}
        w={360}
        h={110}
        color={peakColor}
        color2={t.accentSoft}
        fill="rgba(0,0,0,.04)"
      />
      <div
        style={{
          fontFamily: t.mono,
          fontSize: 11,
          color: t.faint,
          marginTop: 6,
          letterSpacing: 0.4,
        }}
      >
        — — walk night &nbsp; — no walk
      </div>
    </div>
  );
}
