import { callMl } from "@/server/ml/client";
import { analyzeInputSchema, trackAnalysisSchema } from "@/server/ml/schema";
import { protectedProcedure, router } from "../trpc";

export const analyzeRouter = router({
  track: protectedProcedure
    .input(analyzeInputSchema)
    .mutation(({ input }) =>
      callMl("/tracks/search", trackAnalysisSchema, { query: input.query }),
    ),
});
