const VISIBLE = 8;

export function MoodBars({ scores }: { scores: Record<string, number> }) {
  const rows = Object.entries(scores)
    .sort((a, b) => b[1] - a[1])
    .slice(0, VISIBLE);
  const top = rows[0]?.[1] || 1;

  return (
    <ul className="space-y-3">
      {rows.map(([tag, score]) => (
        <li
          key={tag}
          className="grid grid-cols-[6.5rem_minmax(0,1fr)_3rem] items-center gap-3 text-sm"
        >
          <span className="capitalize">{tag}</span>
          <span className="h-2 overflow-hidden rounded-full bg-foreground/10">
            <span
              className="block h-full rounded-full bg-brand transition-[width] duration-700"
              style={{ width: `${Math.round((score / top) * 100)}%` }}
            />
          </span>
          <span className="text-right tabular-nums text-muted-foreground">
            {Math.round(score * 100)}%
          </span>
        </li>
      ))}
    </ul>
  );
}
