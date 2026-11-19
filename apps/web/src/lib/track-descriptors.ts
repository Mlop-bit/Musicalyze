import type { PlaylistTrack } from "@/server/spotify/schema";

export function toDescriptors(tracks: PlaylistTrack[]) {
  return tracks.flatMap((track) =>
    track.id
      ? [
          {
            trackId: track.id,
            title: track.name,
            artist: track.primaryArtist,
            isrc: track.isrc,
          },
        ]
      : [],
  );
}
