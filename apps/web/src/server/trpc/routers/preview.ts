import { z } from "zod";
import { findPreviewUrl } from "@/server/deezer/client";
import { protectedProcedure, router } from "../trpc";

export const previewRouter = router({
  find: protectedProcedure
    .input(
      z.object({
        title: z.string().min(1),
        artist: z.string(),
        isrc: z.string().nullable(),
      }),
    )
    .query(({ input }) => findPreviewUrl(input)),
});
