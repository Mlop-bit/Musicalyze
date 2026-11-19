import { prisma } from "@musicalyze/db";

type JobRecord = {
  id: string;
  userId: string;
  kind: "reorder" | "recommend";
  title: string;
  playlistId: string | null;
};

export function recordJob(job: JobRecord) {
  return prisma.userJob.create({ data: job });
}
