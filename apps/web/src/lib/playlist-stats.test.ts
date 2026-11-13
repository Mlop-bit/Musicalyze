import { describe, expect, it } from "vitest";
import type { PlaylistTrack } from "@/server/spotify/schema";
import { formatDuration, playlistStats, sortByOrder } from "./playlist-stats";

const track = (
  id: string,
  artist: string,
  durationMs: number,
): PlaylistTrack => ({
  id,
  name: id,
  artists: artist,
  primaryArtist: artist,
  isrc: null,
  album: "",
  image: null,
  url: "",
  durationMs,
});

describe("playlistStats", () => {
  it("sums durations and ranks artists", () => {
    const stats = playlistStats([
      track("a", "X", 60_000),
      track("b", "X", 120_000),
      track("c", "Y", 60_000),
    ]);
    expect(stats.totalMs).toBe(240_000);
    expect(stats.uniqueArtists).toBe(2);
    expect(stats.topArtists[0]).toEqual(["X", 2]);
  });
});

describe("sortByOrder", () => {
  it("follows the order and keeps unknown tracks last", () => {
    const sorted = sortByOrder(
      [track("a", "X", 1), track("b", "X", 1), track("c", "X", 1)],
      ["c", "a"],
    );
    expect(sorted.map((item) => item.id)).toEqual(["c", "a", "b"]);
  });
});

describe("formatDuration", () => {
  it("formats minutes and hours", () => {
    expect(formatDuration(185_000)).toBe("3:05");
    expect(formatDuration(3_725_000)).toBe("1:02:05");
  });
});
