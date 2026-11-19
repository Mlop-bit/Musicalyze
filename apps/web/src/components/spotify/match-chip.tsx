import { Tip } from "@/components/ui/tip";

export function MatchChip({ similarity }: { similarity: number }) {
  const percent = Math.round(Math.max(0, Math.min(1, similarity)) * 100);

  return (
    <Tip label="How close the sound is to your starting tracks. 100% would be identical.">
      <span className="shrink-0 rounded-full bg-brand/15 px-2.5 py-0.5 text-xs font-semibold tabular-nums text-brand">
        {percent}% match
      </span>
    </Tip>
  );
}
