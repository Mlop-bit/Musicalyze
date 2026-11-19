import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { PlaylistsApp } from "@/components/spotify/playlists-app";
import { auth } from "@/server/auth/auth";

type Props = {
  searchParams: Promise<{ job?: string; kind?: string; playlist?: string }>;
};

export default async function DashboardPage({ searchParams }: Props) {
  const session = await auth.api.getSession({ headers: await headers() });
  if (!session) redirect("/login");

  const { job, kind, playlist } = await searchParams;
  const resume =
    job && playlist && kind === "reorder"
      ? { jobId: job, kind: "reorder" as const, playlistId: playlist }
      : job && playlist && kind === "recommend"
        ? { jobId: job, kind: "recommend" as const, playlistId: playlist }
        : undefined;

  return <PlaylistsApp key={resume?.jobId} resume={resume} />;
}
