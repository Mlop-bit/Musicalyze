import { initTRPC, TRPCError } from "@trpc/server";
import { auth } from "@/server/auth/auth";
import { getSpotifyAccessToken } from "@/server/spotify/access-token";
import type { Context } from "./context";

const t = initTRPC.context<Context>().create();

export const router = t.router;
export const publicProcedure = t.procedure;
export const createCallerFactory = t.createCallerFactory;

export const protectedProcedure = t.procedure.use(async ({ ctx, next }) => {
  const session = await auth.api.getSession({ headers: ctx.headers });
  if (!session)
    throw new TRPCError({
      code: "UNAUTHORIZED",
      message: "Sign in with Spotify first.",
    });

  const spotifyAccessToken = await getSpotifyAccessToken(
    ctx.headers,
    session.user.id,
  );
  if (!spotifyAccessToken) {
    throw new TRPCError({
      code: "FORBIDDEN",
      message: "No Spotify account is linked.",
    });
  }

  return next({ ctx: { ...ctx, session, spotifyAccessToken } });
});
