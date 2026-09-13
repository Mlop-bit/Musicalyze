import { VerticalTimeline } from "@/components/changelog/vertical-timeline";
import { GITHUB_OWNER, GITHUB_REPO } from "@/server/github/constants";
import { createServerCaller } from "@/server/trpc/caller";

export const revalidate = 3600;

export default async function ChangelogPage() {
  const caller = createServerCaller();
  const [releases, commits] = await Promise.all([
    caller.changelog.getReleases(),
    caller.changelog.getCommits(),
  ]);

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-12 px-6 py-16 sm:px-10">
      <div className="flex flex-col gap-3">
        <h1 className="font-sans text-3xl font-semibold text-foreground sm:text-4xl">
          Changelog
        </h1>
        <p className="max-w-2xl text-sm text-muted-foreground sm:text-base">
          Every commit on the private Mlop-bit/AIProject repository, tracked as
          two lanes: Release follows what ships on{" "}
          <span className="font-mono text-xs">main</span>, and Development
          follows day-to-day work on{" "}
          <span className="font-mono text-xs">development</span> before it
          merges.
        </p>
      </div>
      <VerticalTimeline
        releases={releases}
        commits={commits}
        releaseCompareUrl={`https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}/commits/main`}
        developmentCompareUrl={`https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}/commits/development`}
      />
    </main>
  );
}
