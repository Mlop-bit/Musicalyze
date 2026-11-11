import { prismaAdapter } from "@better-auth/prisma-adapter";
import { prisma } from "@musicalyze/db";
import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";
import { env } from "@/env";

type SpotifyProfile = {
  id: string;
  account_id?: string;
  display_name?: string | null;
  email?: string | null;
  images?: Array<{ url: string }>;
};

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
      ],
      getUserInfo: async ({ accessToken }) => {
        const response = await fetch("https://api.spotify.com/v1/me", {
          headers: { Authorization: `Bearer ${accessToken}` },
          cache: "no-store",
        });
        if (!response.ok) {
          if (process.env.NODE_ENV === "development") {
            console.error(`[Spotify] GET /v1/me failed with HTTP ${response.status}`);
          }
          return null;
        }

        const profile = (await response.json()) as SpotifyProfile;
        const identity = profile.account_id ?? profile.id;
        return {
          user: {
            name: profile.display_name || `Spotify user ${identity}`,
            email: profile.email || `spotify-${identity}@users.musicalyze.invalid`,
            image: profile.images?.[0]?.url,
            emailVerified: false,
          },
          data: profile,
        };
      },
    },
  },
  plugins: [nextCookies()],
});
