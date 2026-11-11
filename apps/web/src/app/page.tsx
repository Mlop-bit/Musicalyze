import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { SpotifyHome } from "@/components/spotify/spotify-home";

export default async function Home() {
  if (process.env.NODE_ENV === "development") {
    const host = (await headers()).get("host")?.split(":")[0];
    if (host === "localhost") {
      redirect("http://127.0.0.1:3000");
    }
  }

  return <SpotifyHome />;
}
