import { describe, expect, it } from "vitest";
import { toPlaylistTrack } from "./library";

describe("toPlaylistTrack", () => {
  it("joins the artists and keeps the first one as primary", () => {
    const track = toPlaylistTrack({
      id: "a",
      name: "Song",
      duration_ms: 1000,
      artists: [{ name: "One" }, { name: "Two" }],
      album: { name: "Album", images: [{ url: "https://img" }] },
      external_urls: { spotify: "https://open.spotify.com/track/a" },
      external_ids: { isrc: "XX1" },
    });
    expect(track).toMatchObject({
      artists: "One, Two",
      primaryArtist: "One",
      isrc: "XX1",
      image: "https://img",
    });
  });

  it("tolerates a track without artwork or isrc", () => {
    const track = toPlaylistTrack({
      id: null,
      name: "Local file",
      duration_ms: 1,
      artists: [],
      album: { name: "", images: [] },
      external_urls: { spotify: "" },
    });
    expect(track).toMatchObject({ primaryArtist: "", isrc: null, image: null });
  });
});
