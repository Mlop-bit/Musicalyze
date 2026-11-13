import { moodColor } from "@/lib/mood-color";

type Props = { label: string | null; level: number | null };

export function MoodChip({ label, level }: Props) {
  if (label === null && level === null) return null;

  return (
    <span className="hidden shrink-0 items-center gap-1.5 rounded-full bg-foreground/[0.06] px-2.5 py-0.5 text-xs capitalize text-muted-foreground sm:flex">
      <span
        className="size-2 rounded-full"
        style={{ background: moodColor(level ?? 0.5) }}
      />
      {label ?? "mixed"}
    </span>
  );
}
