import { describe, expect, it } from "vitest";
import type { CommitEntry } from "@/server/github/schema";
import { formatDay, groupByDay, parseCommitMessage } from "./commit-groups";

const commit = (sha: string, date: string): CommitEntry => ({
  sha,
  shortSha: sha,
  message: "feat: x",
  coAuthors: [],
  author: "a",
  date,
  htmlUrl: "https://example.com",
});

describe("parseCommitMessage", () => {
  it("splits a conventional commit", () => {
    expect(parseCommitMessage("feat(web): add feed")).toEqual({
      type: "feat",
      title: "add feed",
    });
  });

  it("keeps free text untyped", () => {
    expect(parseCommitMessage("updating next.js")).toEqual({
      type: null,
      title: "updating next.js",
    });
  });
});

describe("formatDay", () => {
  it("formats a day in English without depending on the time zone", () => {
    expect(formatDay("2026-11-12")).toBe("Thursday, November 12");
  });
});

describe("groupByDay", () => {
  it("groups commits by calendar day in order", () => {
    const days = groupByDay([
      commit("a", "2026-11-12T10:00:00Z"),
      commit("b", "2026-11-12T08:00:00Z"),
      commit("c", "2026-11-10T08:00:00Z"),
    ]);
    expect(days.map((day) => [day.day, day.commits.length])).toEqual([
      ["2026-11-12", 2],
      ["2026-11-10", 1],
    ]);
  });
});
