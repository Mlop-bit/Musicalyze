import { z } from "zod";
import { callMl } from "@/server/ml/client";
import {
  jobCreatedSchema,
  jobViewSchema,
  reorderInputSchema,
} from "@/server/ml/schema";
import { protectedProcedure, router } from "../trpc";

export const moodRouter = router({
  reorder: protectedProcedure
    .input(reorderInputSchema)
    .mutation(async ({ ctx, input }) => {
      const created = await callMl("/jobs/reorder", jobCreatedSchema, {
        user_id: ctx.session.user.id,
        tracks: input.tracks.map(({ trackId, title, artist, isrc }) => ({
          track_id: trackId,
          title,
          artist,
          isrc,
        })),
        start_track_id: input.startTrackId ?? null,
        mode: input.mode,
      });
      return { jobId: created.job_id };
    }),

  job: protectedProcedure
    .input(z.object({ jobId: z.uuid() }))
    .query(({ input }) => callMl(`/jobs/${input.jobId}`, jobViewSchema)),
});
