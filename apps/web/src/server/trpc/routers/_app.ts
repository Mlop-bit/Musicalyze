import { router } from "../trpc";
import { changelogRouter } from "./changelog";

export const appRouter = router({
  changelog: changelogRouter,
});

export type AppRouter = typeof appRouter;
