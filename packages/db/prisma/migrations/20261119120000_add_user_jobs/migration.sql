CREATE TABLE "user_jobs" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "kind" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "playlistId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "user_jobs_pkey" PRIMARY KEY ("id")
);

CREATE INDEX "user_jobs_userId_createdAt_idx" ON "user_jobs"("userId", "createdAt");

ALTER TABLE "user_jobs" ADD CONSTRAINT "user_jobs_userId_fkey" FOREIGN KEY ("userId") REFERENCES "user"("id") ON DELETE CASCADE ON UPDATE CASCADE;
