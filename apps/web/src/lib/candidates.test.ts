import { describe, expect, it } from "vitest";
import type { PlaylistTrack } from "@/server/spotify/schema";
import { pickCandidates } from "./candidates";

const track = (id: string | null): PlaylistTrack => ({
  id,
  name: id ?? "local",
  artists: "A",
  primaryArtist: "A",
  isrc: null,
  album: "",
  image: null,
  url: "",
  durationMs: 1,
});

const ids = (tracks: PlaylistTrack[]) => tracks.map((entry) => entry.id);

describe("pickCandidates", () => {
  it("excludes seeds, duplicates and tracks without an id", () => {
    const picked = pickCandidates(
      [track("s")],
      [
        [track("s"), track("a"), track(null)],
        [track("a"), track("b")],
      ],
    );
    expect(ids(picked)).toEqual(["a", "b"]);
  });

  it("interleaves the pools so one playlist cannot fill the cap", () => {
    const picked = pickCandidates(
      [],
      [
        [track("a1"), track("a2"), track("a3")],
        [track("b1"), track("b2")],
      ],
      4,
    );
    expect(ids(picked)).toEqual(["a1", "b1", "a2", "b2"]);
  });
});
