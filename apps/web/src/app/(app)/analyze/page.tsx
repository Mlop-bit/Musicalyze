import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { TrackAnalyzer } from "@/components/analyze/track-analyzer";
import { auth } from "@/server/auth/auth";

export default async function AnalyzePage() {
  const session = await auth.api.getSession({ headers: await headers() });
  if (!session) redirect("/login");

  return <TrackAnalyzer />;
}
