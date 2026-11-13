import CountUp from "@/components/react-bits/CountUp";
import { formatDuration, type playlistStats } from "@/lib/playlist-stats";

type Stats = ReturnType<typeof playlistStats>;

function Stat({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="px-4 text-center">
      <dt className="text-[0.65rem] uppercase tracking-wider text-muted-foreground">
        {label}
      </dt>
      <dd className="text-base font-semibold tabular-nums">{children}</dd>
    </div>
  );
}

export function BarStats({ stats }: { stats: Stats }) {
  return (
    <dl className="relative hidden divide-x divide-border rounded-2xl bg-foreground/[0.05] py-1.5 ring-1 ring-border lg:flex">
      <Stat label="tracks">
        <CountUp to={stats.count} duration={1.2} />
      </Stat>
      <Stat label="artists">
        <CountUp to={stats.uniqueArtists} duration={1.2} />
      </Stat>
      <Stat label="total">{formatDuration(stats.totalMs)}</Stat>
      <Stat label="avg">{formatDuration(stats.averageMs)}</Stat>
    </dl>
  );
}
