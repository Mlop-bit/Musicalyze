import { z } from "zod";

const envSchema = z.object({
  MUSICALYZE_GITHUB_TOKEN: z.string().min(1),
  BETTER_AUTH_SECRET: z.string().min(1),
  BETTER_AUTH_URL: z.url(),
  SPOTIFY_CLIENT_ID: z.string().min(1),
  SPOTIFY_CLIENT_SECRET: z.string().min(1),
  MUSICALYZE_API_KEY: z.string().min(1),
  MUSICALYZE_ML_API_URL: z.url().default("http://127.0.0.1:8000"),
});

export const env = envSchema.parse({
  MUSICALYZE_GITHUB_TOKEN: process.env.MUSICALYZE_GITHUB_TOKEN,
  BETTER_AUTH_SECRET: process.env.BETTER_AUTH_SECRET,
  BETTER_AUTH_URL: process.env.BETTER_AUTH_URL,
  SPOTIFY_CLIENT_ID: process.env.SPOTIFY_CLIENT_ID,
  SPOTIFY_CLIENT_SECRET: process.env.SPOTIFY_CLIENT_SECRET,
  MUSICALYZE_API_KEY: process.env.MUSICALYZE_API_KEY,
  MUSICALYZE_ML_API_URL: process.env.MUSICALYZE_ML_API_URL,
});
