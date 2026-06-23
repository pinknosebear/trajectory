export default function Dots({ value, onChange, label }) {
  return (
    <div className="dots" aria-label={label}>
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          key={n}
          type="button"
          className={n <= value ? "dot is-on" : "dot"}
          aria-label={`${label} ${n}`}
          onClick={() => onChange(n)}
        />
      ))}
    </div>
  );
}
