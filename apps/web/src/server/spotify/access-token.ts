import { prisma } from "@musicalyze/db";
import { auth } from "@/server/auth/auth";

export async function getSpotifyAccessToken(headers: Headers, userId: string) {
  const account = await prisma.account.findFirst({
    where: { userId, providerId: "spotify" },
    select: { id: true },
  });
  if (!account) return null;

  const { accessToken } = await auth.api.getAccessToken({
    body: { accountId: account.id },
    headers,
  });
  return accessToken;
}
