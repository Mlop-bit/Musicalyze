import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { PlaylistsApp } from "@/components/spotify/playlists-app";
import { auth } from "@/server/auth/auth";

export default async function DashboardPage() {
  const session = await auth.api.getSession({ headers: await headers() });
  if (!session) redirect("/login");

  return <PlaylistsApp />;
}
