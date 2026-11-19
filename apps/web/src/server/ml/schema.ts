import { z } from "zod";
import { reorderModeSchema } from "@/lib/reorder-modes";

export const jobCreatedSchema = z.object({ job_id: z.uuid() });

export const trackDetailSchema = z.object({
  track_id: z.string(),
  mood_label: z.string().nullable(),
  energy: z.number().nullable(),
});

const jobBase = z.object({
  job_id: z.uuid(),
  status: z.enum(["queued", "running", "succeeded", "failed"]),
  phase: z.enum(["resolving", "computing"]).nullable(),
  done: z.number(),
  total: z.number(),
  error: z.string().nullable(),
});

export const jobViewSchema = jobBase.extend({
  result: z
    .looseObject({
      order: z.array(z.string()),
      skipped: z.array(z.string()),
      details: z.array(trackDetailSchema).default([]),
    })
    .nullable(),
});

export const recommendJobViewSchema = jobBase.extend({
  result: z
    .looseObject({
      recommendations: z.array(
        z.object({ track_id: z.string(), similarity: z.number() }),
      ),
      skipped: z.array(z.string()),
      dropped_candidates: z.number(),
    })
    .nullable(),
});

export const splitClusterSchema = z.object({
  name: z.string(),
  track_ids: z.array(z.string()),
});

export const splitJobViewSchema = jobBase.extend({
  result: z
    .looseObject({
      clusters: z.array(splitClusterSchema),
      k: z.number(),
      skipped: z.array(z.string()),
    })
    .nullable(),
});

export const trackAnalysisSchema = z.object({
  track_id: z.string(),
  musicbrainz_id: z.string().nullable(),
  bpm: z.number().nullable(),
  key: z.string().nullable(),
  mood_label: z.string().nullable(),
  mood_scores: z.record(z.string(), z.number()).nullable(),
  source: z.string().nullable(),
});

export const analyzeInputSchema = z.object({
  query: z.string().trim().min(2).max(200),
});

export const jobListSchema = z.array(
  jobBase.extend({
    kind: z.enum(["reorder", "split", "recommend"]),
    created_at: z.string(),
  }),
);

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
  playlistId: z.string().min(1),
  playlistName: z.string().min(1).max(200),
  mode: reorderModeSchema.default("similarity"),
});

export const splitInputSchema = z.object({
  tracks: z
    .array(
      z.object({
        trackId: z.string().min(1),
        title: z.string(),
        artist: z.string(),
        isrc: z.string().nullable(),
      }),
    )
    .min(6)
    .max(500),
  k: z.number().int().min(2).max(8).optional(),
  playlistId: z.string().min(1),
  playlistName: z.string().min(1).max(200),
});

export type TrackDetail = z.infer<typeof trackDetailSchema>;
export type TrackAnalysis = z.infer<typeof trackAnalysisSchema>;
export type JobView = z.infer<typeof jobViewSchema>;
export type ReorderInput = z.infer<typeof reorderInputSchema>;

export type SplitCluster = z.infer<typeof splitClusterSchema>;
export type SplitJobView = z.infer<typeof splitJobViewSchema>;
export type SplitInput = z.infer<typeof splitInputSchema>;
