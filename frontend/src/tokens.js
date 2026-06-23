// Design tokens — mirrors the Tweaks panel from the HTML mockups.
// Change `ACCENT`, `SURFACE`, or `HEADLINE` to re-skin the whole app, or wire
// these to a settings endpoint to make them user-controlled.

const ACCENTS = {
  terracotta: { h: 24, s: 72, l: 55 },
  blue: { h: 255, s: 76, l: 56 },
  evergreen: { h: 160, s: 45, l: 48 },
  plum: { h: 288, s: 35, l: 52 },
};

const SURFACES = {
  warm: { h: 30, s: 16, l: 97 },
  neutral: { h: 0, s: 0, l: 98 },
  cool: { h: 220, s: 9, l: 97.5 },
};

export function buildTokens({
  accent = "terracotta",
  surface = "warm",
  headline = "editorial",
} = {}) {
  const a = ACCENTS[accent] || ACCENTS.terracotta;
  const s = SURFACES[surface] || SURFACES.warm;
  return {
    bg: `hsl(${s.h}, ${s.s}%, ${s.l}%)`,
    paper: `hsl(${s.h}, ${s.s + 2}%, 99.5%)`,
    ink: "#1a1a1a",
    ink2: "#333",
    soft: "#666",
    faint: "#999",
    line: `hsl(${s.h}, ${s.s}%, 88%)`,
    accent: `hsl(${a.h}, ${a.s}%, ${a.l}%)`,
    accentSoft: `hsl(${a.h}, ${a.s}%, 92%)`,
    accentDeep: `hsl(${a.h}, ${a.s}%, ${Math.max(a.l - 16, 24)}%)`,
    onAccent: "#fff",
    good: "#16a34a",
    warn: "#b45309",
    danger: "#dc2626",
    sidebar: "#24201d",
    sidebarInk: "rgba(255,255,255,.76)",
    display: headline === "editorial" ? "Newsreader" : "Public Sans",
    body: "'Public Sans', sans-serif",
    mono: "'IBM Plex Mono', monospace",
    headW: headline === "editorial" ? 600 : 700,
    headLS: headline === "editorial" ? 0 : -0.5,
  };
}
