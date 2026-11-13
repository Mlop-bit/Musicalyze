"use client";

import { ExternalLink } from "lucide-react";
import { m } from "motion/react";
import { useMemo, useState } from "react";
import { Segmented } from "@/components/ui/segmented";
import { formatDay, groupByDay, parseCommitMessage } from "@/lib/commit-groups";
import { formatRelativeDate } from "@/lib/format-relative-date";
import type { CommitEntry } from "@/server/github/schema";

type Lane = "release" | "development";

const TYPE_STYLE: Record<string, string> = {
  feat: "bg-brand/20 text-brand",
  fix: "bg-red-500/15 text-red-500",
  refactor: "bg-sky-500/15 text-sky-500",
  docs: "bg-amber-500/15 text-amber-500",
  chore: "bg-foreground/10 text-muted-foreground",
  test: "bg-foreground/10 text-muted-foreground",
};

type Props = { releases: CommitEntry[]; commits: CommitEntry[] };

export function ChangelogFeed({ releases, commits }: Props) {
  const [lane, setLane] = useState<Lane>("development");
  const entries = lane === "release" ? releases : commits;
  const days = useMemo(() => groupByDay(entries), [entries]);

  return (
    <div className="space-y-8">
      <Segmented
        value={lane}
        onValueChange={setLane}
        label="Branch"
        options={[
          { value: "development", label: `Development · ${commits.length}` },
          { value: "release", label: `Release · ${releases.length}` },
        ]}
      />
      <div className="space-y-10">
        {days.map(({ day, commits: dayCommits }) => (
          <section
            key={`${lane}-${day}`}
            className="grid gap-4 md:grid-cols-[19rem_minmax(0,1fr)]"
          >
            <h2 className="font-script text-4xl leading-none text-brand md:sticky md:top-24 md:self-start">
              {formatDay(day)}
            </h2>
            <ul className="surface divide-y divide-border overflow-hidden rounded-3xl backdrop-blur-xl">
              {dayCommits.map((commit, index) => {
                const { type, title } = parseCommitMessage(commit.message);
                return (
                  <m.li
                    key={commit.sha}
                    initial={{ opacity: 0, y: 12 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: "-40px" }}
                    transition={{
                      duration: 0.45,
                      delay: Math.min(index, 6) * 0.05,
                      ease: [0.16, 1, 0.3, 1],
                    }}
                  >
                    <a
                      href={commit.htmlUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="group flex items-center gap-3 px-4 py-3 transition-colors hover:bg-accent/60"
                    >
                      {type && (
                        <span
                          className={`w-16 shrink-0 rounded-full py-0.5 text-center text-xs font-semibold ${TYPE_STYLE[type] ?? TYPE_STYLE.chore}`}
                        >
                          {type}
                        </span>
                      )}
                      <span className="min-w-0 flex-1">
                        <span className="block truncate font-medium">
                          {title}
                        </span>
                        <span className="block truncate text-xs text-muted-foreground">
                          {commit.author}
                          {commit.coAuthors.length > 0
                            ? ` + ${commit.coAuthors.join(", ")}`
                            : ""}{" "}
                          · {formatRelativeDate(commit.date)}
                        </span>
                      </span>
                      <span className="hidden font-mono text-xs text-muted-foreground sm:block">
                        {commit.shortSha}
                      </span>
                      <ExternalLink className="size-3.5 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
                    </a>
                  </m.li>
                );
              })}
            </ul>
          </section>
        ))}
      </div>
    </div>
  );
}
