import { router } from "../trpc";
import { changelogRouter } from "./changelog";
import { moodRouter } from "./mood";
import { previewRouter } from "./preview";
import { spotifyRouter } from "./spotify";

export const appRouter = router({
  changelog: changelogRouter,
  mood: moodRouter,
  preview: previewRouter,
  spotify: spotifyRouter,
});

export type AppRouter = typeof appRouter;
