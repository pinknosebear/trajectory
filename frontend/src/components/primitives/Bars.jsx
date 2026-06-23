export default function Bars({ data = [] }) {
  if (!data.length) return null;
  const max = Math.max(...data, 1);
  return (
    <div className="bars" aria-hidden="true">
      {data.map((value, index) => (
        <span key={`${value}-${index}`} style={{ height: `${(value / max) * 100}%` }} />
      ))}
    </div>
  );
}
