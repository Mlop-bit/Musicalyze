import { prisma } from "@musicalyze/db";
import { z } from "zod";
import { callMl } from "@/server/ml/client";
import { jobListSchema } from "@/server/ml/schema";
import { protectedProcedure, router } from "../trpc";

const RECENT_JOBS = 20;

export const jobsRouter = router({
  list: protectedProcedure.query(async ({ ctx }) => {
    const userId = ctx.session.user.id;
    const [records, states] = await Promise.all([
      prisma.userJob.findMany({
        where: { userId },
        orderBy: { createdAt: "desc" },
        take: RECENT_JOBS,
      }),
      callMl(`/jobs?user_id=${encodeURIComponent(userId)}`, jobListSchema),
    ]);
    const byId = new Map(states.map((state) => [state.job_id, state]));
    return records.flatMap((record) => {
      const state = byId.get(record.id);
      return state
        ? [
            {
              id: record.id,
              kind: record.kind,
              title: record.title,
              playlistId: record.playlistId,
              createdAt: record.createdAt.toISOString(),
              status: state.status,
              phase: state.phase,
              done: state.done,
              total: state.total,
              error: state.error,
            },
          ]
        : [];
    });
  }),

  remove: protectedProcedure
    .input(z.object({ jobId: z.uuid() }))
    .mutation(({ ctx, input }) =>
      prisma.userJob.deleteMany({
        where: { id: input.jobId, userId: ctx.session.user.id },
      }),
    ),
});
