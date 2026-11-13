import type { CommitEntry } from "@/server/github/schema";

export type CommitDay = { day: string; commits: CommitEntry[] };

const TYPE_PATTERN = /^(\w+)(?:\([^)]*\))?!?:\s*(.*)$/;

const DAY_FORMAT = new Intl.DateTimeFormat("en", {
  weekday: "long",
  day: "numeric",
  month: "long",
  timeZone: "UTC",
});

export function formatDay(day: string) {
  return DAY_FORMAT.format(new Date(`${day}T00:00:00Z`));
}

export function parseCommitMessage(message: string) {
  const match = TYPE_PATTERN.exec(message);
  return match
    ? { type: match[1].toLowerCase(), title: match[2] }
    : { type: null, title: message };
}

export function groupByDay(commits: CommitEntry[]): CommitDay[] {
  const days = new Map<string, CommitEntry[]>();
  for (const commit of commits) {
    const day = commit.date.slice(0, 10);
    days.set(day, [...(days.get(day) ?? []), commit]);
  }
  return [...days].map(([day, entries]) => ({ day, commits: entries }));
}
