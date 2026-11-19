import { prisma } from "@musicalyze/db";
import { TRPCError } from "@trpc/server";

type JobRecord = {
  id: string;
  userId: string;
  kind: "reorder" | "recommend" | "split";
  title: string;
  playlistId: string | null;
};

export function recordJob(job: JobRecord) {
  return prisma.userJob.create({ data: job });
}

export async function assertJobOwner(userId: string, jobId: string) {
  const owned = await prisma.userJob.findFirst({
    where: { id: jobId, userId },
    select: { id: true },
  });
  if (!owned)
    throw new TRPCError({ code: "NOT_FOUND", message: "Job not found." });
}
