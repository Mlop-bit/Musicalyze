import { z } from "zod";
import { REORDER_MODES } from "@/lib/reorder-modes";
import { recordJob } from "@/server/jobs/record";
import { callMl } from "@/server/ml/client";
import {
  jobCreatedSchema,
  jobViewSchema,
  reorderInputSchema,
  splitInputSchema,
  splitJobViewSchema,
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
      const modeLabel =
        REORDER_MODES.find((mode) => mode.value === input.mode)?.label ??
        input.mode;
      await recordJob({
        id: created.job_id,
        userId: ctx.session.user.id,
        kind: "reorder",
        title: `${modeLabel} · ${input.playlistName}`,
        playlistId: input.playlistId,
      });
      return { jobId: created.job_id };
    }),

  job: protectedProcedure
    .input(z.object({ jobId: z.uuid() }))
    .query(({ input }) => callMl(`/jobs/${input.jobId}`, jobViewSchema)),

  split: protectedProcedure
    .input(splitInputSchema)
    .mutation(async ({ ctx, input }) => {
      const created = await callMl("/jobs/split", jobCreatedSchema, {
        user_id: ctx.session.user.id,
        tracks: input.tracks.map(({ trackId, title, artist, isrc }) => ({
          track_id: trackId,
          title,
          artist,
          isrc,
        })),
        k: input.k ?? null,
      });
      await recordJob({
        id: created.job_id,
        userId: ctx.session.user.id,
        kind: "split",
        title: `Split · ${input.playlistName}`,
        playlistId: input.playlistId,
      });
      return { jobId: created.job_id };
    }),

  splitJob: protectedProcedure
    .input(z.object({ jobId: z.uuid() }))
    .query(({ input }) => callMl(`/jobs/${input.jobId}`, splitJobViewSchema)),
});
