"use client";

import { useQueryClient } from "@tanstack/react-query";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import type { PlaylistTrack } from "@/server/spotify/schema";
import { useTRPC } from "@/trpc/client";

type Status = "idle" | "loading" | "playing" | "unavailable";

type Player = {
  keyOf: (track: PlaylistTrack) => string;
  statusOf: (track: PlaylistTrack) => Status;
  toggle: (track: PlaylistTrack) => void;
};

const PlayerContext = createContext<Player | null>(null);

export function PreviewProvider({ children }: { children: React.ReactNode }) {
  const trpc = useTRPC();
  const queryClient = useQueryClient();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [active, setActive] = useState<{ key: string; status: Status } | null>(
    null,
  );

  useEffect(() => {
    const audio = new Audio();
    const onEnded = () => setActive(null);
    audio.addEventListener("ended", onEnded);
    audioRef.current = audio;
    return () => {
      audio.removeEventListener("ended", onEnded);
      audio.pause();
      audioRef.current = null;
    };
  }, []);

  const keyOf = useCallback(
    (track: PlaylistTrack) => track.id ?? `${track.name}-${track.artists}`,
    [],
  );

  const statusOf = useCallback(
    (track: PlaylistTrack): Status =>
      active?.key === keyOf(track) ? active.status : "idle",
    [active, keyOf],
  );

  const toggle = useCallback(
    async (track: PlaylistTrack) => {
      const audio = audioRef.current;
      const key = keyOf(track);
      if (!audio) return;
      if (active?.key === key && active.status === "playing") {
        audio.pause();
        setActive(null);
        return;
      }
      audio.pause();
      setActive({ key, status: "loading" });
      try {
        const url = await queryClient.fetchQuery(
          trpc.preview.find.queryOptions({
            title: track.name,
            artist: track.primaryArtist,
            isrc: track.isrc,
          }),
        );
        if (!url) {
          setActive({ key, status: "unavailable" });
          return;
        }
        audio.src = url;
        await audio.play();
        setActive({ key, status: "playing" });
      } catch {
        setActive({ key, status: "unavailable" });
      }
    },
    [active, keyOf, queryClient, trpc],
  );

  const value = useMemo(
    () => ({ keyOf, statusOf, toggle }),
    [keyOf, statusOf, toggle],
  );

  return <PlayerContext value={value}>{children}</PlayerContext>;
}

export function usePreview() {
  const context = useContext(PlayerContext);
  if (!context)
    throw new Error("usePreview must be used inside PreviewProvider");
  return context;
}
