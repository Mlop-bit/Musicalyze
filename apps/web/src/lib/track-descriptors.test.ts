import { describe, expect, it } from "vitest";
import type { PlaylistTrack } from "@/server/spotify/schema";
import { toDescriptors } from "./track-descriptors";

const track = (id: string | null): PlaylistTrack => ({
  id,
  name: "Song",
  artists: "A, B",
  primaryArtist: "A",
  isrc: "XX1",
  album: "",
  image: null,
  url: "",
  durationMs: 1,
});

describe("toDescriptors", () => {
  it("keeps the primary artist and the isrc", () => {
    expect(toDescriptors([track("a")])).toEqual([
      { trackId: "a", title: "Song", artist: "A", isrc: "XX1" },
    ]);
  });

  it("drops tracks without a Spotify id", () => {
    expect(toDescriptors([track(null), track("b")])).toHaveLength(1);
  });
});
