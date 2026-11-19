export function MatchChip({ similarity }: { similarity: number }) {
  const percent = Math.round(Math.max(0, Math.min(1, similarity)) * 100);

  return (
    <span className="shrink-0 rounded-full bg-brand/15 px-2.5 py-0.5 text-xs font-semibold tabular-nums text-brand">
      {percent}% match
    </span>
  );
}
