import { prismaAdapter } from "@better-auth/prisma-adapter";
import { prisma } from "@musicalyze/db";
import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";
import { env } from "@/env";
import { spotifyProfileSchema } from "@/server/spotify/schema";

export const auth = betterAuth({
  baseURL: env.BETTER_AUTH_URL,
  secret: env.BETTER_AUTH_SECRET,
  database: prismaAdapter(prisma, {
    provider: "postgresql",
  }),
  socialProviders: {
    spotify: {
      clientId: env.SPOTIFY_CLIENT_ID,
      clientSecret: env.SPOTIFY_CLIENT_SECRET,
      scope: [
        "user-read-email",
        "user-read-private",
        "playlist-read-private",
        "playlist-read-collaborative",
        "user-library-read",
        "playlist-modify-public",
        "playlist-modify-private",
      ],
      getUserInfo: async ({ accessToken }) => {
        const response = await fetch("https://api.spotify.com/v1/me", {
          headers: { Authorization: `Bearer ${accessToken}` },
          cache: "no-store",
        });
        if (!response.ok) {
          if (process.env.NODE_ENV === "development") {
            console.error(
              `[Spotify] GET /v1/me failed with HTTP ${response.status}`,
            );
          }
          return null;
        }

        const profile = spotifyProfileSchema.parse(await response.json());
        const identity = profile.account_id ?? profile.id;
        const name = profile.display_name || `Spotify user ${identity}`;
        const email =
          profile.email || `spotify-${identity}@users.musicalyze.invalid`;
        return {
          user: {
            name,
            email,
            image: profile.images[0]?.url,
            emailVerified: false,
          },
          data: { ...profile, display_name: name, email },
        };
      },
    },
  },
  plugins: [nextCookies()],
});
