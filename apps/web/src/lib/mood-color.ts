const CALM_HUE = 205;
const ENERGETIC_HUE = 115;

export function moodColor(level: number) {
  const clamped = Math.min(1, Math.max(0, level));
  return `hsl(${CALM_HUE + (ENERGETIC_HUE - CALM_HUE) * clamped} 78% 52%)`;
}

export function normalizeLevels(values: Array<number | null>) {
  const known = values.filter((value): value is number => value !== null);
  if (known.length === 0) return values.map(() => null);
  const low = Math.min(...known);
  const span = Math.max(...known) - low;
  return values.map((value) =>
    value === null ? null : span === 0 ? 0.5 : (value - low) / span,
  );
}
