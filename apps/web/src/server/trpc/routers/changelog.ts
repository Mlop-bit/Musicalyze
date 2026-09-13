import { fetchBranchCommits } from "../../github/client";
import { publicProcedure, router } from "../trpc";

export const changelogRouter = router({
  getReleases: publicProcedure.query(() => fetchBranchCommits("main")),
  getCommits: publicProcedure.query(() => fetchBranchCommits("development")),
});
