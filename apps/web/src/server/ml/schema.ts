import { z } from "zod";
import { reorderModeSchema } from "@/lib/reorder-modes";

export const jobCreatedSchema = z.object({ job_id: z.uuid() });

export const trackDetailSchema = z.object({
  track_id: z.string(),
  mood_label: z.string().nullable(),
  energy: z.number().nullable(),
});

export const jobViewSchema = z.object({
  job_id: z.uuid(),
  status: z.enum(["queued", "running", "succeeded", "failed"]),
  phase: z.enum(["resolving", "computing"]).nullable(),
  done: z.number(),
  total: z.number(),
  error: z.string().nullable(),
  result: z
    .looseObject({
      order: z.array(z.string()),
      skipped: z.array(z.string()),
      details: z.array(trackDetailSchema).default([]),
    })
    .nullable(),
});

export const reorderInputSchema = z.object({
  tracks: z
    .array(
      z.object({
        trackId: z.string().min(1),
        title: z.string(),
        artist: z.string(),
        isrc: z.string().nullable(),
      }),
    )
    .min(2)
    .max(500),
  startTrackId: z.string().min(1).optional(),
  mode: reorderModeSchema.default("similarity"),
});

export type TrackDetail = z.infer<typeof trackDetailSchema>;
export type JobView = z.infer<typeof jobViewSchema>;
export type ReorderInput = z.infer<typeof reorderInputSchema>;
