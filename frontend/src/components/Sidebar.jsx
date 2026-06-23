const nav = [
  ["Overview", true],
  ["Coach", true],
  ["Goals", false],
  ["Glucose", false],
  ["Labs", false],
  ["Trends", false],
  ["Correlations", false],
  ["Experiments", false],
  ["Daily Log", false],
  ["Learn", false],
  ["Weekly Summary", false],
];

export default function Sidebar({ view, onViewChange }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark">↗</span>
        <span>Trajectory</span>
      </div>
      <nav className="side-nav">
        {nav.map(([label, enabled]) => (
          <button
            key={label}
            className={view === label ? "active" : ""}
            type="button"
            disabled={!enabled}
            onClick={() => enabled && onViewChange(label)}
          >
            {label}
          </button>
        ))}
      </nav>
      <div className="profile-chip">
        <span>R</span>
        <div>
          <strong>Ravi</strong>
          <small>Local profile</small>
        </div>
      </div>
    </aside>
  );
}
