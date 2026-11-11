import { headers } from "next/headers";
import { auth } from "@/server/auth/auth";
import { prisma } from "@musicalyze/db";

export async function getSpotifyAccessToken() {
  const requestHeaders = await headers();
  const session = await auth.api.getSession({ headers: requestHeaders });
  if (!session) return null;

  const account = await prisma.account.findFirst({
    where: { userId: session.user.id, providerId: "spotify" },
    select: { id: true },
  });
  if (!account) return null;

  const token = await auth.api.getAccessToken({
    body: { accountId: account.id },
    headers: requestHeaders,
  });
  return token.accessToken;
}
