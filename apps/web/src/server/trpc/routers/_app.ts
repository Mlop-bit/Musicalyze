import { router } from "../trpc";
import { analyzeRouter } from "./analyze";
import { changelogRouter } from "./changelog";
import { jobsRouter } from "./jobs";
import { moodRouter } from "./mood";
import { previewRouter } from "./preview";
import { recommendRouter } from "./recommend";
import { spotifyRouter } from "./spotify";

export const appRouter = router({
  analyze: analyzeRouter,
  changelog: changelogRouter,
  jobs: jobsRouter,
  mood: moodRouter,
  preview: previewRouter,
  recommend: recommendRouter,
  spotify: spotifyRouter,
});

export type AppRouter = typeof appRouter;
