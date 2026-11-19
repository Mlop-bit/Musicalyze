import { describe, expect, it } from "vitest";
import type { PlaylistTrack } from "@/server/spotify/schema";
import { topArtists } from "./discover";

const seed = (primaryArtist: string): PlaylistTrack => ({
  id: primaryArtist,
  name: "Song",
  artists: primaryArtist,
  primaryArtist,
  isrc: null,
  album: "",
  image: null,
  url: "",
  durationMs: 1,
});

describe("topArtists", () => {
  it("ranks artists by how often they appear", () => {
    const artists = topArtists([
      seed("A"),
      seed("B"),
      seed("B"),
      seed("C"),
      seed("B"),
      seed("A"),
    ]);
    expect(artists.slice(0, 2)).toEqual(["B", "A"]);
  });

  it("keeps at most five and skips empty names", () => {
    const seeds = ["a", "b", "c", "d", "e", "f", ""].map(seed);
    expect(topArtists(seeds)).toHaveLength(5);
  });
});
