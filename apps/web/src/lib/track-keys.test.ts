import { describe, expect, it } from "vitest";
import type { PlaylistTrack } from "@/server/spotify/schema";
import { withKeys } from "./track-keys";

const track = (id: string | null, name: string): PlaylistTrack => ({
  id,
  name,
  artists: "A",
  primaryArtist: "A",
  isrc: null,
  album: "",
  image: null,
  url: "",
  durationMs: 1,
});

describe("withKeys", () => {
  it("gives repeated tracks distinct keys", () => {
    const keys = withKeys([
      track("a", "x"),
      track("a", "x"),
      track("b", "y"),
    ]).map((entry) => entry.key);
    expect(new Set(keys).size).toBe(3);
  });

  it("falls back to name and artists for tracks without an id", () => {
    expect(withKeys([track(null, "x")])[0].key).toBe("x-A-0");
  });
});
