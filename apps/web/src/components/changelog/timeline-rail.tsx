import type { RefObject } from "react";
import { Badge } from "@/components/ui/badge";
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyTitle,
} from "@/components/ui/empty";
import { formatRelativeDate } from "@/lib/format-relative-date";
import { cn } from "@/lib/utils";
import type { CommitEntry } from "@/server/github/schema";
import { LINE_X, type RailTheme } from "./changelog-themes";

export type TimelineRailProps = {
  theme: RailTheme;
  entries: CommitEntry[];
  positions: Map<string, number>;
  trackHeight: number;
  trackRef: RefObject<HTMLDivElement | null>;
  pathRef: RefObject<SVGPathElement | null>;
  cardRefs: RefObject<Map<string, HTMLElement>>;
  compareUrl: string;
};

export function TimelineRail({
  theme,
  entries,
  positions,
  trackHeight,
  trackRef,
  pathRef,
  cardRefs,
  compareUrl,
}: TimelineRailProps) {
  return (
    <section className="flex min-w-0 flex-col gap-4">
      <h2
        className={cn(
          "font-mono text-xs tracking-[0.2em] uppercase",
          theme.textClass,
        )}
      >
        {theme.label}
      </h2>
      {entries.length === 0 ? (
        <Empty>
          <EmptyHeader>
            <EmptyTitle>No commits yet</EmptyTitle>
            <EmptyDescription>Nothing on this branch yet.</EmptyDescription>
          </EmptyHeader>
        </Empty>
      ) : (
        <div
          ref={trackRef}
          className="relative"
          style={{ height: trackHeight }}
        >
          <svg
            aria-hidden="true"
            focusable="false"
            className="absolute inset-0 h-full w-full overflow-visible"
          >
            <path
              ref={pathRef}
              d={`M ${LINE_X} 0 L ${LINE_X} ${trackHeight}`}
              className={cn("fill-none", theme.strokeClass)}
              strokeWidth={2}
              strokeLinecap="round"
            />
          </svg>
          {entries.map((entry) => {
            const y = positions.get(entry.sha) ?? 0;
            const authorLine =
              entry.coAuthors.length > 0
                ? [entry.author, ...entry.coAuthors].join("/")
                : entry.author;
            return (
              <a
                key={entry.sha}
                ref={(el) => {
                  if (el) cardRefs.current.set(entry.sha, el);
                  else cardRefs.current.delete(entry.sha);
                }}
                href={entry.htmlUrl}
                target="_blank"
                rel="noreferrer"
                style={{ top: y }}
                className="absolute inset-x-0 flex min-w-0 items-start rounded-sm pl-6 sm:pl-7"
              >
                <span
                  aria-hidden="true"
                  className={cn(
                    "absolute top-1.5 size-2.5 shrink-0 rounded-full",
                    theme.dotClass,
                  )}
                  style={{ left: LINE_X - 5 }}
                />
                <div className="flex min-w-0 flex-1 flex-col gap-1">
                  <div className="flex min-w-0 flex-nowrap items-center gap-2">
                    <Badge
                      variant="outline"
                      className={cn("font-mono text-[11px]", theme.badgeClass)}
                    >
                      {entry.shortSha}
                    </Badge>
                    <span className="min-w-0 truncate font-mono text-[11px] text-muted-foreground">
                      {formatRelativeDate(entry.date)}
                    </span>
                  </div>
                  <p className="min-w-0 truncate text-sm text-foreground">
                    {entry.message}
                  </p>
                  <span className="min-w-0 truncate text-xs text-muted-foreground">
                    {authorLine}
                  </span>
                </div>
              </a>
            );
          })}
        </div>
      )}
      <a
        href={compareUrl}
        target="_blank"
        rel="noreferrer"
        className="text-xs text-muted-foreground underline underline-offset-4 hover:text-foreground"
      >
        View all on GitHub
      </a>
    </section>
  );
}
