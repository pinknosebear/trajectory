// Inline SVG sparkline / curve. Pass `data` (array of numbers), optional
// second series `data2` for the walk-vs-no-walk overlay.
export default function Sparkline({
  data,
  data2 = null,
  w = 360,
  h = 110,
  color = "#888",
  color2 = "#bbb",
  fill = "none",
  dot = false,
}) {
  if (!data || data.length === 0) return null;
  const all = data2 ? data.concat(data2) : data;
  const min = Math.min(...all);
  const max = Math.max(...all);
  const pad = 6;
  const span = max - min || 1;

  const toPath = (series) =>
    series
      .map((v, i) => {
        const x = pad + (i / (series.length - 1)) * (w - pad * 2);
        const y = pad + (1 - (v - min) / span) * (h - pad * 2);
        return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(" ");

  const lastX = w - pad;
  const lastY = pad + (1 - (data[data.length - 1] - min) / span) * (h - pad * 2);

  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ display: "block" }}>
      {fill !== "none" && (
        <path
          d={`${toPath(data)} L${lastX},${h - pad} L${pad},${h - pad} Z`}
          fill={fill}
          stroke="none"
        />
      )}
      {data2 && (
        <path
          d={toPath(data2)}
          fill="none"
          stroke={color2}
          strokeWidth="2"
          strokeDasharray="5 4"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      )}
      <path
        d={toPath(data)}
        fill="none"
        stroke={color}
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {dot && <circle cx={lastX} cy={lastY} r="3.5" fill={color} />}
    </svg>
  );
}
